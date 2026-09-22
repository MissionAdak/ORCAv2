import json
import sys
from datetime import datetime
from urllib.request import Request, urlopen

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
)


API_BASE = "http://127.0.0.1:8000"


def fetch_mission_package(incident_id):
    url = f"{API_BASE}/api/sar/{incident_id}/mission-package"

    request = Request(
        url,
        data=b"",
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def safe(value, default="N/A"):
    if value is None or value == "":
        return default
    return str(value)


def format_number(value, digits=3):
    if value is None or value == "":
        return "N/A"

    try:
        return f"{float(value):.{digits}f}"
    except (TypeError, ValueError):
        return safe(value)


def format_percent(value):
    if value is None or value == "":
        return "N/A"

    try:
        return f"{float(value) * 100:.1f}%"
    except (TypeError, ValueError):
        return safe(value)


def normalize_list(value):
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, dict):
        for key in (
            "zones",
            "search_zones",
            "items",
            "results",
            "data",
        ):
            nested = value.get(key)

            if isinstance(nested, list):
                return nested

        if any(
            key in value
            for key in (
                "id",
                "zone_id",
                "probability",
                "risk_score",
                "priority",
                "geometry",
            )
        ):
            return [value]

    return []


def get_incident(package, fallback_incident_id):
    incident = package.get("incident")

    if not isinstance(incident, dict):
        incident = package.get("sar_incident")

    if not isinstance(incident, dict):
        incident = {}

    return {
        "id": (
            incident.get("id")
            or incident.get("incident_id")
            or package.get("incident_id")
            or fallback_incident_id
        ),
        "status": incident.get("status"),
        "latitude": (
            incident.get("last_known_latitude")
            if incident.get("last_known_latitude") is not None
            else incident.get("latitude")
        ),
        "longitude": (
            incident.get("last_known_longitude")
            if incident.get("last_known_longitude") is not None
            else incident.get("longitude")
        ),
        "created_at": incident.get("created_at"),
    }


def get_zones(package):
    search_zones = package.get("search_zones")

    if search_zones is None:
        search_zones = package.get("zones")

    return normalize_list(search_zones)


def get_prioritization(package):
    search_zones = package.get("search_zones")

    if isinstance(search_zones, dict):
        return search_zones.get("prioritization")

    return None


def get_rescue(package):
    rescue = package.get("rescue")

    if not isinstance(rescue, dict):
        rescue = {}

    facility = rescue.get("nearest_rescue_facility")

    if not isinstance(facility, dict):
        facility = {}

    return {
        "facility": facility,
        "distance_km": rescue.get("distance_km"),
        "bearing_degrees": rescue.get("bearing_degrees"),
        "route_geometry": rescue.get("route_geometry"),
        "hazard_check": rescue.get("hazard_check"),
    }


def get_evidence(package):
    evidence = package.get("evidence")

    if isinstance(evidence, dict):
        items = evidence.get("items")

        if isinstance(items, list):
            return items

    if isinstance(evidence, list):
        return evidence

    return []


def priority_text(priority):
    return safe(priority, "N/A").upper()


def build_styles():
    styles = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "ORCATitle",
            parent=styles["Title"],
            fontSize=22,
            leading=26,
            alignment=TA_CENTER,
            spaceAfter=6,
        ),
        "subtitle": ParagraphStyle(
            "ORCASubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "section": ParagraphStyle(
            "ORCASection",
            parent=styles["Heading2"],
            fontSize=15,
            leading=18,
            spaceBefore=8,
            spaceAfter=9,
        ),
        "normal": ParagraphStyle(
            "ORCANormal",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
        ),
        "small": ParagraphStyle(
            "ORCASmall",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=10,
        ),
        "table": ParagraphStyle(
            "ORCATable",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=9,
        ),
        "table_bold": ParagraphStyle(
            "ORCATableBold",
            parent=styles["Normal"],
            fontSize=7.5,
            leading=9,
            fontName="Helvetica-Bold",
        ),
        "warning": ParagraphStyle(
            "ORCAWarning",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
        ),
    }


def P(text, style):
    return Paragraph(
        str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"),
        style,
    )


def add_header(story, package, incident):
    styles = build_styles()

    story.append(
        P("ORCA SAR MISSION BRIEF", styles["title"])
    )

    story.append(
        P(
            "Search and Rescue Operational Package",
            styles["subtitle"],
        )
    )

    status = safe(
        package.get("status"),
        "SAR mission package generated",
    )

    header_table = Table(
        [
            [
                P("<b>Incident ID</b>", styles["table"]),
                P("<b>Status</b>", styles["table"]),
                P("<b>Generated</b>", styles["table"]),
            ],
            [
                P(safe(incident.get("id")), styles["table"]),
                P(status, styles["table"]),
                P(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    styles["table"],
                ),
            ],
        ],
        colWidths=[55 * mm, 70 * mm, 55 * mm],
    )

    header_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e8ed")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#b8c0ca")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d2d7de")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(header_table)
    story.append(Spacer(1, 8 * mm))


def add_incident(story, incident):
    styles = build_styles()

    story.append(
        P("1. Incident", styles["section"])
    )

    data = [
        [
            P("<b>Incident ID</b>", styles["table"]),
            P("<b>Status</b>", styles["table"]),
            P("<b>Last Known Latitude</b>", styles["table"]),
            P("<b>Last Known Longitude</b>", styles["table"]),
            P("<b>Created</b>", styles["table"]),
        ],
        [
            P(safe(incident.get("id")), styles["table"]),
            P(safe(incident.get("status")), styles["table"]),
            P(format_number(incident.get("latitude"), 6), styles["table"]),
            P(format_number(incident.get("longitude"), 6), styles["table"]),
            P(safe(incident.get("created_at")), styles["small"]),
        ],
    ]

    table = Table(
        data,
        colWidths=[28 * mm, 28 * mm, 38 * mm, 38 * mm, 48 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e8ed")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#b8c0ca")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d2d7de")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 5 * mm))


def add_zones(story, package):
    styles = build_styles()

    story.append(
        P("2. Prioritized SAR Search Zones", styles["section"])
    )

    zones = get_zones(package)

    data = [
        [
            P("<b>#</b>", styles["table_bold"]),
            P("<b>Zone ID</b>", styles["table_bold"]),
            P("<b>Probability</b>", styles["table_bold"]),
            P("<b>Risk Score</b>", styles["table_bold"]),
            P("<b>Priority</b>", styles["table_bold"]),
            P("<b>Recommended Action</b>", styles["table_bold"]),
        ]
    ]

    for index, zone in enumerate(zones, start=1):
        if not isinstance(zone, dict):
            continue

        zone_id = (
            zone.get("id")
            or zone.get("zone_id")
            or zone.get("search_zone_id")
        )

        risk_score = zone.get("risk_score")

        if risk_score is None:
            risk_score = zone.get("probability_weighted_risk")

        data.append(
            [
                P(index, styles["table"]),
                P(safe(zone_id), styles["table"]),
                P(format_percent(zone.get("probability")), styles["table_bold"]),
                P(format_number(risk_score, 4), styles["table"]),
                P(priority_text(zone.get("priority")), styles["table"]),
                P(
                    safe(zone.get("recommended_action")),
                    styles["small"],
                ),
            ]
        )

    if len(data) == 1:
        data.append(
            [
                P("-", styles["table"]),
                P("No data", styles["table"]),
                P("-", styles["table"]),
                P("-", styles["table"]),
                P("-", styles["table"]),
                P("No SAR search-zone data available.", styles["small"]),
            ]
        )

    table = Table(
        data,
        colWidths=[
            10 * mm,
            22 * mm,
            27 * mm,
            25 * mm,
            25 * mm,
            70 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e8ed")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#b8c0ca")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d2d7de")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(table)

    prioritization = get_prioritization(package)

    if prioritization:
        story.append(Spacer(1, 3 * mm))
        story.append(
            P(
                f"<b>Prioritization:</b> {prioritization}",
                styles["small"],
            )
        )

    story.append(Spacer(1, 5 * mm))


def add_rescue(story, package):
    styles = build_styles()
    rescue = get_rescue(package)
    facility = rescue["facility"]

    story.append(
        P("3. Rescue Facility", styles["section"])
    )

    if not facility:
        story.append(
            P("No rescue facility data available.", styles["normal"])
        )
        return

    data = [
        [
            P("<b>Facility</b>", styles["table_bold"]),
            P("<b>Type</b>", styles["table_bold"]),
            P("<b>Latitude</b>", styles["table_bold"]),
            P("<b>Longitude</b>", styles["table_bold"]),
        ],
        [
            P(safe(facility.get("name")), styles["table"]),
            P(safe(facility.get("type")), styles["table"]),
            P(format_number(facility.get("latitude"), 6), styles["table"]),
            P(format_number(facility.get("longitude"), 6), styles["table"]),
        ],
    ]

    table = Table(
        data,
        colWidths=[55 * mm, 55 * mm, 40 * mm, 40 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e8ed")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#b8c0ca")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d2d7de")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 3 * mm))

    summary = Table(
        [
            [
                P("<b>Distance</b>", styles["table_bold"]),
                P("<b>Bearing</b>", styles["table_bold"]),
            ],
            [
                P(
                    f"{format_number(rescue.get('distance_km'), 3)} km",
                    styles["table"],
                ),
                P(
                    f"{format_number(rescue.get('bearing_degrees'), 1)}°",
                    styles["table"],
                ),
            ],
        ],
        colWidths=[90 * mm, 90 * mm],
    )

    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f3f6")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c6ccd4")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d2d7de")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(summary)
    story.append(Spacer(1, 5 * mm))


def add_route(story, package):
    styles = build_styles()
    rescue = get_rescue(package)
    geometry = rescue.get("route_geometry")

    story.append(
        P("4. Rescue Route", styles["section"])
    )

    if not isinstance(geometry, dict):
        story.append(
            P("No rescue route data available.", styles["normal"])
        )
        return

    coordinates = geometry.get("coordinates", [])

    coordinate_text = []

    if isinstance(coordinates, list):
        for point in coordinates:
            if isinstance(point, list) and len(point) >= 2:
                try:
                    coordinate_text.append(
                        f"{float(point[1]):.6f}, {float(point[0]):.6f}"
                    )
                except (TypeError, ValueError):
                    pass

    route_text = " → ".join(coordinate_text)

    if not route_text:
        route_text = "N/A"

    data = [
        [
            P("<b>Geometry Type</b>", styles["table_bold"]),
            P("<b>Distance</b>", styles["table_bold"]),
            P("<b>Bearing</b>", styles["table_bold"]),
        ],
        [
            P(safe(geometry.get("type")), styles["table"]),
            P(
                f"{format_number(rescue.get('distance_km'), 3)} km",
                styles["table"],
            ),
            P(
                f"{format_number(rescue.get('bearing_degrees'), 1)}°",
                styles["table"],
            ),
        ],
    ]

    table = Table(
        data,
        colWidths=[60 * mm, 60 * mm, 60 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e8ed")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#b8c0ca")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d2d7de")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 3 * mm))

    story.append(
        P(
            f"<b>Route coordinates:</b> {route_text}",
            styles["small"],
        )
    )

    story.append(Spacer(1, 5 * mm))


def add_hazard(story, package):
    styles = build_styles()
    rescue = get_rescue(package)
    hazard = rescue.get("hazard_check")

    story.append(
        P("5. Rescue Route Hazard Check", styles["section"])
    )

    if not isinstance(hazard, dict):
        story.append(
            P(
                "No rescue-route hazard check available.",
                styles["normal"],
            )
        )
        return

    intersects = hazard.get("intersects")
    status = safe(hazard.get("status"))
    message = safe(hazard.get("message"))

    if intersects is True:
        result = "HAZARD INTERSECTION DETECTED"
    elif intersects is False:
        result = "NO HAZARD INTERSECTION"
    else:
        result = status

    data = [
        [
            P("<b>Result</b>", styles["table_bold"]),
            P("<b>Status</b>", styles["table_bold"]),
        ],
        [
            P(result, styles["table_bold"]),
            P(status, styles["table"]),
        ],
    ]

    table = Table(
        data,
        colWidths=[90 * mm, 90 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e8ed")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#b8c0ca")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d2d7de")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 3 * mm))

    story.append(
        P(
            f"<b>Message:</b> {message}",
            styles["small"],
        )
    )

    story.append(Spacer(1, 5 * mm))


def add_evidence(story, package):
    styles = build_styles()

    story.append(
        P("6. SAR Evidence", styles["section"])
    )

    evidence = get_evidence(package)

    data = [
        [
            P("<b>Type</b>", styles["table_bold"]),
            P("<b>Description</b>", styles["table_bold"]),
            P("<b>Source</b>", styles["table_bold"]),
            P("<b>Source Timestamp</b>", styles["table_bold"]),
            P("<b>Confidence</b>", styles["table_bold"]),
        ]
    ]

    for item in evidence:
        if not isinstance(item, dict):
            continue

        confidence = item.get("confidence")

        data.append(
            [
                P(
                    safe(
                        item.get("evidence_type")
                        or item.get("type")
                    ),
                    styles["small"],
                ),
                P(
                    safe(item.get("description")),
                    styles["small"],
                ),
                P(
                    safe(item.get("source")),
                    styles["small"],
                ),
                P(
                    safe(item.get("source_timestamp")),
                    styles["small"],
                ),
                P(
                    format_number(confidence, 2),
                    styles["small"],
                ),
            ]
        )

    if len(data) == 1:
        data.append(
            [
                P("N/A", styles["small"]),
                P("No SAR evidence available.", styles["small"]),
                P("N/A", styles["small"]),
                P("N/A", styles["small"]),
                P("N/A", styles["small"]),
            ]
        )

    table = Table(
        data,
        colWidths=[
            32 * mm,
            65 * mm,
            30 * mm,
            38 * mm,
            20 * mm,
        ],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e8ed")),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#b8c0ca")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d2d7de")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 5 * mm))


def add_warning(story, package):
    styles = build_styles()

    story.append(
        P("7. Operational Warning", styles["section"])
    )

    warning = package.get("estimate_warning")

    if not warning:
        warning = (
            "SAR search zones are planning estimates based on available "
            "data and are not exact survivor locations."
        )

    table = Table(
        [
            [
                P(
                    f"<b>{warning}</b>",
                    styles["warning"],
                )
            ]
        ],
        colWidths=[185 * mm],
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff7ed")),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#e07b00")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        )
    )

    story.append(table)


def add_footer(canvas, doc):
    canvas.saveState()

    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.HexColor("#68788d"))

    canvas.drawCentredString(
        A4[0] / 2,
        10 * mm,
        f"ORCA SAR Mission Brief  |  Page {doc.page}",
    )

    canvas.restoreState()


def create_pdf(package, incident_id, output_file):
    incident = get_incident(package, incident_id)

    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=16 * mm,
        title=f"ORCA SAR Mission Brief - Incident {incident_id}",
        author="ORCA SAR System",
    )

    story = []

    add_header(story, package, incident)
    add_incident(story, incident)
    add_zones(story, package)
    add_rescue(story, package)
    add_route(story, package)
    add_hazard(story, package)
    add_evidence(story, package)
    add_warning(story, package)

    doc.build(
        story,
        onFirstPage=add_footer,
        onLaterPages=add_footer,
    )


def main():
    incident_id = 3

    if len(sys.argv) > 1:
        try:
            incident_id = int(sys.argv[1])
        except ValueError:
            print("Invalid incident ID.")
            return 1

    output_file = "sar_mission_brief.pdf"

    print()
    print("ORCA SAR MISSION BRIEF - PDF EXPORT")
    print()
    print(f"Incident ID : {incident_id}")
    print("Fetching mission package...")
    print()

    try:
        package = fetch_mission_package(incident_id)
    except Exception as exc:
        print("ERROR: Could not fetch mission package.")
        print(str(exc))
        return 1

    try:
        create_pdf(
            package,
            incident_id,
            output_file,
        )
    except Exception as exc:
        print("ERROR: Could not create PDF.")
        print(str(exc))
        return 1

    print("PDF MISSION BRIEF CREATED")
    print()
    print(f"Output : {output_file}")
    print()
    print("Sections:")
    print("- Incident")
    print("- Prioritized SAR search zones")
    print("- Rescue facility")
    print("- Rescue route")
    print("- Route hazard check")
    print("- SAR evidence")
    print("- Operational warning")
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())