"""
ORCA SAR Operational Dashboard
Offline-safe map dashboard.

This version does NOT request OpenStreetMap tiles, avoiding tile-server 403 errors
when the HTML file is opened directly from the local filesystem.
"""

import json
import sqlite3
import folium
from folium import Element


DB_PATH = "orca_cache.db"
OUTPUT_FILE = "sar_dashboard.html"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def load_incidents():
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            id,
            status,
            last_known_latitude,
            last_known_longitude,
            created_at
        FROM sar_incidents
        ORDER BY id DESC
        """
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def load_zones(incident_id):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            id,
            geometry,
            probability,
            risk_score,
            priority,
            recommended_action,
            created_at
        FROM sar_search_zones
        WHERE incident_id = ?
        ORDER BY
            CASE priority
                WHEN 'HIGH' THEN 1
                WHEN 'MEDIUM' THEN 2
                WHEN 'LOW' THEN 3
                ELSE 4
            END,
            probability DESC,
            risk_score DESC
        """,
        (incident_id,),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def parse_geometry(value):
    if not value:
        return None

    try:
        return json.loads(value)
    except Exception:
        return None


def geometry_points(geometry):
    points = []

    if not geometry:
        return points

    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates")

    def walk(value):
        if (
            isinstance(value, list)
            and len(value) == 2
            and isinstance(value[0], (int, float))
            and isinstance(value[1], (int, float))
        ):
            points.append((float(value[1]), float(value[0])))
            return

        if isinstance(value, list):
            for item in value:
                walk(item)

    if geometry_type in ("Polygon", "MultiPolygon", "LineString", "MultiLineString"):
        walk(coordinates)

    return points


def center_from_incident(incident):
    latitude = incident.get("last_known_latitude")
    longitude = incident.get("last_known_longitude")

    if latitude is None or longitude is None:
        return 20.0, 78.0

    return float(latitude), float(longitude)


def priority_color(priority):
    if priority == "HIGH":
        return "red"

    if priority == "MEDIUM":
        return "orange"

    if priority == "LOW":
        return "green"

    return "blue"


def add_coordinate_grid(fmap, min_lat, max_lat, min_lon, max_lon):
    lat_step = 0.02
    lon_step = 0.02

    latitude = min_lat
    while latitude <= max_lat + 0.0001:
        folium.PolyLine(
            [
                [latitude, min_lon],
                [latitude, max_lon],
            ],
            weight=1,
            opacity=0.18,
        ).add_to(fmap)

        latitude += lat_step

    longitude = min_lon
    while longitude <= max_lon + 0.0001:
        folium.PolyLine(
            [
                [min_lat, longitude],
                [max_lat, longitude],
            ],
            weight=1,
            opacity=0.18,
        ).add_to(fmap)

        longitude += lon_step


def build_map(incident, zones):
    incident_lat, incident_lon = center_from_incident(incident)

    all_points = [
        (incident_lat, incident_lon)
    ]

    parsed_zones = []

    for zone in zones:
        geometry = parse_geometry(zone.get("geometry"))

        if geometry:
            parsed_zones.append((zone, geometry))
            all_points.extend(geometry_points(geometry))

    if all_points:
        min_lat = min(point[0] for point in all_points)
        max_lat = max(point[0] for point in all_points)
        min_lon = min(point[1] for point in all_points)
        max_lon = max(point[1] for point in all_points)

        lat_padding = max((max_lat - min_lat) * 0.15, 0.03)
        lon_padding = max((max_lon - min_lon) * 0.15, 0.03)

        min_lat -= lat_padding
        max_lat += lat_padding
        min_lon -= lon_padding
        max_lon += lon_padding
    else:
        min_lat = incident_lat - 0.10
        max_lat = incident_lat + 0.10
        min_lon = incident_lon - 0.10
        max_lon = incident_lon + 0.10

    fmap = folium.Map(
        location=[incident_lat, incident_lon],
        zoom_start=10,
        tiles=None,
        control_scale=True,
    )

    add_coordinate_grid(
        fmap,
        min_lat,
        max_lat,
        min_lon,
        max_lon,
    )

    incident_popup = f"""
    <div style="font-size:14px;">
        <b>ORCA SAR INCIDENT</b><br><br>
        <b>ID:</b> {incident.get("id")}<br>
        <b>Status:</b> {incident.get("status")}<br>
        <b>Latitude:</b> {incident_lat:.6f}<br>
        <b>Longitude:</b> {incident_lon:.6f}<br>
        <b>Created:</b> {incident.get("created_at")}
    </div>
    """

    folium.Marker(
        [incident_lat, incident_lon],
        popup=folium.Popup(
            incident_popup,
            max_width=350,
        ),
        tooltip="SAR Incident",
        icon=folium.Icon(
            icon="exclamation-sign",
            prefix="glyphicon",
            color="black",
        ),
    ).add_to(fmap)

    for index, (zone, geometry) in enumerate(
        parsed_zones,
        start=1,
    ):
        probability = zone.get("probability")
        risk_score = zone.get("risk_score")
        priority = zone.get("priority")
        action = zone.get("recommended_action")

        probability_text = (
            f"{float(probability) * 100:.1f}%"
            if probability is not None
            else "N/A"
        )

        risk_text = (
            f"{float(risk_score):.4f}"
            if risk_score is not None
            else "N/A"
        )

        popup_html = f"""
        <div style="font-size:14px;">
            <b>SAR SEARCH ZONE #{index}</b><br><br>

            <b>Zone ID:</b> {zone.get("id")}<br>
            <b>Probability:</b> {probability_text}<br>
            <b>Risk Score:</b> {risk_text}<br>
            <b>Priority:</b> {priority or "N/A"}<br><br>

            <b>Recommended Action:</b><br>
            {action or "N/A"}
        </div>
        """

        color = priority_color(priority)

        folium.GeoJson(
            geometry,
            name=f"Search Zone {index}",
            style_function=lambda feature, color=color: {
                "fillColor": color,
                "color": color,
                "weight": 3,
                "fillOpacity": 0.35,
            },
            highlight_function=lambda feature: {
                "weight": 5,
                "fillOpacity": 0.55,
            },
            tooltip=folium.Tooltip(
                f"Zone {index} | "
                f"Probability {probability_text} | "
                f"Risk {risk_text} | "
                f"Priority {priority or 'N/A'}"
            ),
            popup=folium.Popup(
                popup_html,
                max_width=400,
            ),
        ).add_to(fmap)

    folium.LayerControl().add_to(fmap)

    dashboard_html = f"""
    <div id="orca-dashboard"
         style="
         position: fixed;
         top: 15px;
         right: 15px;
         z-index: 9999;
         background: white;
         padding: 15px;
         border-radius: 8px;
         box-shadow: 0 2px 8px rgba(0,0,0,0.25);
         font-family: Arial;
         min-width: 260px;
         ">

        <div style="font-size:20px;font-weight:bold;">
            ORCA SAR
        </div>

        <div style="font-size:13px;margin-top:5px;">
            Operational Search Dashboard
        </div>

        <hr>

        <div><b>Incident:</b> {incident.get("id")}</div>
        <div><b>Status:</b> {incident.get("status")}</div>
        <div><b>Search Zones:</b> {len(zones)}</div>

        <hr>

        <div>
            <span style="
                display:inline-block;
                width:12px;
                height:12px;
                background:red;
                margin-right:6px;
            "></span>
            HIGH Priority
        </div>

        <div>
            <span style="
                display:inline-block;
                width:12px;
                height:12px;
                background:orange;
                margin-right:6px;
            "></span>
            MEDIUM Priority
        </div>

        <div>
            <span style="
                display:inline-block;
                width:12px;
                height:12px;
                background:green;
                margin-right:6px;
            "></span>
            LOW Priority
        </div>

        <hr>

        <div style="font-size:12px;">
            Base map tiles are disabled for offline-safe operation.
            <br><br>
            Click a zone for probability, risk and action.
        </div>

    </div>
    """

    fmap.get_root().html.add_child(
        Element(dashboard_html)
    )

    fmap.fit_bounds(
        [
            [min_lat, min_lon],
            [max_lat, max_lon],
        ]
    )

    return fmap


def main():
    incidents = load_incidents()

    if not incidents:
        print("No SAR incidents found.")
        return

    incident = incidents[0]

    zones = load_zones(
        incident["id"]
    )

    fmap = build_map(
        incident,
        zones,
    )

    fmap.save(
        OUTPUT_FILE
    )

    print()
    print("ORCA SAR DASHBOARD CREATED")
    print()
    print(f"Incident ID : {incident['id']}")
    print(f"Zones       : {len(zones)}")
    print(f"Output      : {OUTPUT_FILE}")
    print()
    print("Offline-safe map generated.")
    print("Open sar_dashboard.html in your browser.")


if __name__ == "__main__":
    main()
