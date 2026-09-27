"""
ORCA SAR Mission Brief Exporter

Generates an operator-friendly HTML mission brief
from the SAR mission package API response.
"""

import json
import sys
from datetime import datetime
from html import escape
from urllib.request import Request, urlopen


API_BASE = "http://127.0.0.1:8000"
DEFAULT_INCIDENT_ID = 3
DEFAULT_OUTPUT = "sar_mission_brief.html"


def fetch_mission_package(incident_id):
    url = f"{API_BASE}/api/sar/{incident_id}/mission-package"

    request = Request(
        url,
        method="POST",
        headers={
            "Accept": "application/json",
        },
    )

    with urlopen(request, timeout=30) as response:
        return json.loads(
            response.read().decode("utf-8")
        )


def safe(value, default="N/A"):
    if value is None or value == "":
        return default

    if isinstance(value, (dict, list)):
        return json.dumps(
            value,
            indent=2,
            ensure_ascii=False,
        )

    return str(value)


def format_percent(value):
    if value is None:
        return "N/A"

    try:
        return f"{float(value) * 100:.1f}%"
    except Exception:
        return safe(value)


def format_number(value, digits=4):
    if value is None:
        return "N/A"

    try:
        return f"{float(value):.{digits}f}"
    except Exception:
        return safe(value)


def priority_class(priority):
    priority = str(priority or "").upper()

    if priority == "HIGH":
        return "high"

    if priority == "MEDIUM":
        return "medium"

    if priority == "LOW":
        return "low"

    return "unknown"


def build_zone_rows(zones):
    rows = ""

    for index, zone in enumerate(zones, start=1):
        priority = safe(zone.get("priority"))
        priority_css = priority_class(
            zone.get("priority")
        )

        probability = format_percent(
            zone.get("probability")
        )

        risk_score = format_number(
            zone.get("risk_score")
        )

        action = safe(
            zone.get("recommended_action")
        )

        zone_id = safe(
            zone.get("id")
        )

        rows += f"""
        <tr>
            <td>{index}</td>
            <td>{escape(zone_id)}</td>
            <td><strong>{escape(probability)}</strong></td>
            <td>{escape(risk_score)}</td>
            <td>
                <span class="priority {priority_css}">
                    {escape(priority)}
                </span>
            </td>
            <td>{escape(action)}</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="6">
                No SAR search zones available.
            </td>
        </tr>
        """

    return rows


def build_evidence_rows(evidence):
    rows = ""

    for item in evidence:
        evidence_type = safe(
            item.get("evidence_type")
        )

        description = safe(
            item.get("description")
        )

        source = safe(
            item.get("source")
        )

        timestamp = safe(
            item.get("source_timestamp")
        )

        confidence = safe(
            item.get("confidence")
        )

        rows += f"""
        <tr>
            <td>{escape(evidence_type)}</td>
            <td>{escape(description)}</td>
            <td>{escape(source)}</td>
            <td>{escape(timestamp)}</td>
            <td>{escape(confidence)}</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="5">
                No SAR evidence available.
            </td>
        </tr>
        """

    return rows


def build_rescue_section(rescue_facility):
    if not rescue_facility:
        return """
        <div class="empty">
            No rescue facility data available.
        </div>
        """

    facility_name = safe(
        rescue_facility.get("name")
    )

    latitude = format_number(
        rescue_facility.get("latitude"),
        6,
    )

    longitude = format_number(
        rescue_facility.get("longitude"),
        6,
    )

    distance = format_number(
        rescue_facility.get("distance_km"),
        2,
    )

    return f"""
    <div class="grid">
        <div class="card">
            <div class="label">FACILITY</div>
            <div class="value">
                {escape(facility_name)}
            </div>
        </div>

        <div class="card">
            <div class="label">DISTANCE</div>
            <div class="value">
                {escape(distance)} km
            </div>
        </div>

        <div class="card">
            <div class="label">LATITUDE</div>
            <div class="value">
                {escape(latitude)}
            </div>
        </div>

        <div class="card">
            <div class="label">LONGITUDE</div>
            <div class="value">
                {escape(longitude)}
            </div>
        </div>
    </div>
    """


def build_route_section(rescue_route):
    if not rescue_route:
        return """
        <div class="empty">
            No rescue route data available.
        </div>
        """

    route_geometry = rescue_route.get(
        "route_geometry"
    )

    distance = rescue_route.get(
        "distance_km"
    )

    duration = rescue_route.get(
        "estimated_duration_minutes"
    )

    route_text = (
        json.dumps(
            route_geometry,
            indent=2,
            ensure_ascii=False,
        )
        if route_geometry
        else "N/A"
    )

    return f"""
    <div class="grid">
        <div class="card">
            <div class="label">ROUTE DISTANCE</div>
            <div class="value">
                {escape(format_number(distance, 2))} km
            </div>
        </div>

        <div class="card">
            <div class="label">ESTIMATED DURATION</div>
            <div class="value">
                {escape(format_number(duration, 1))} min
            </div>
        </div>
    </div>

    <details>
        <summary>Route Geometry</summary>
        <pre>{escape(route_text)}</pre>
    </details>
    """


def build_hazard_section(hazard_check):
    if not hazard_check:
        return """
        <div class="empty">
            No rescue-route hazard check available.
        </div>
        """

    return f"""
    <pre>{escape(
        json.dumps(
            hazard_check,
            indent=2,
            ensure_ascii=False,
        )
    )}</pre>
    """


def build_incident_section(incident):
    if not incident:
        return """
        <div class="empty">
            No incident data available.
        </div>
        """

    incident_id = safe(
        incident.get("id")
    )

    status = safe(
        incident.get("status")
    )

    latitude = format_number(
        incident.get("last_known_latitude"),
        6,
    )

    longitude = format_number(
        incident.get("last_known_longitude"),
        6,
    )

    created_at = safe(
        incident.get("created_at")
    )

    return f"""
    <div class="grid">
        <div class="card">
            <div class="label">INCIDENT ID</div>
            <div class="value">
                {escape(incident_id)}
            </div>
        </div>

        <div class="card">
            <div class="label">STATUS</div>
            <div class="value">
                {escape(status)}
            </div>
        </div>

        <div class="card">
            <div class="label">LAST KNOWN LATITUDE</div>
            <div class="value">
                {escape(latitude)}
            </div>
        </div>

        <div class="card">
            <div class="label">LAST KNOWN LONGITUDE</div>
            <div class="value">
                {escape(longitude)}
            </div>
        </div>

        <div class="card">
            <div class="label">CREATED</div>
            <div class="value">
                {escape(created_at)}
            </div>
        </div>
    </div>
    """


def build_html(package):
    incident = package.get("incident") or {}
    zones = package.get("search_zones") or []
    rescue_facility = package.get(
        "rescue_facility"
    )
    rescue_route = package.get(
        "rescue_route"
    )
    hazard_check = package.get(
        "rescue_route_hazard_check"
    )
    evidence = package.get("evidence") or []

    status = safe(
        package.get("status"),
        "SAR mission package generated",
    )

    warning = safe(
        package.get("estimate_warning"),
        "SAR search zones are planning estimates.",
    )

    generated_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    zone_rows = build_zone_rows(zones)
    evidence_rows = build_evidence_rows(evidence)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>
ORCA SAR Mission Brief
</title>

<style>

body {{
    margin: 0;
    padding: 0;
    background: #f2f4f7;
    color: #20242a;
    font-family:
        Arial,
        Helvetica,
        sans-serif;
}}

.container {{
    max-width: 1180px;
    margin: 0 auto;
    padding: 28px;
}}

.header {{
    background: #111827;
    color: white;
    padding: 28px;
    border-radius: 10px;
    margin-bottom: 22px;
}}

.header h1 {{
    margin: 0;
    font-size: 30px;
}}

.header p {{
    margin: 8px 0 0;
    opacity: 0.8;
}}

.status {{
    display: inline-block;
    margin-top: 16px;
    padding: 7px 12px;
    border-radius: 16px;
    background: #166534;
    color: white;
    font-size: 12px;
    font-weight: bold;
}}

.section {{
    background: white;
    padding: 22px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow:
        0 2px 7px rgba(0,0,0,0.08);
}}

.section h2 {{
    margin-top: 0;
    font-size: 20px;
}}

.grid {{
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(190px, 1fr));
    gap: 12px;
}}

.card {{
    border: 1px solid #d9dde3;
    border-radius: 8px;
    padding: 14px;
    background: #fafafa;
}}

.label {{
    font-size: 10px;
    color: #6b7280;
    font-weight: bold;
    letter-spacing: 0.6px;
}}

.value {{
    margin-top: 7px;
    font-size: 16px;
    font-weight: bold;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}}

th {{
    background: #e5e7eb;
    text-align: left;
    padding: 10px;
}}

td {{
    border-bottom: 1px solid #e5e7eb;
    padding: 10px;
    vertical-align: top;
}}

.priority {{
    display: inline-block;
    padding: 4px 9px;
    border-radius: 12px;
    color: white;
    font-size: 10px;
    font-weight: bold;
}}

.priority.high {{
    background: #dc2626;
}}

.priority.medium {{
    background: #d97706;
}}

.priority.low {{
    background: #15803d;
}}

.priority.unknown {{
    background: #6b7280;
}}

.warning {{
    border-left: 5px solid #d97706;
    background: #fff7ed;
    padding: 15px;
    border-radius: 6px;
    font-size: 13px;
}}

.empty {{
    padding: 15px;
    background: #f3f4f6;
    border-radius: 6px;
}}

pre {{
    overflow-x: auto;
    background: #111827;
    color: #f9fafb;
    padding: 15px;
    border-radius: 7px;
    font-size: 11px;
}}

details {{
    margin-top: 15px;
}}

summary {{
    cursor: pointer;
    font-weight: bold;
}}

.footer {{
    text-align: center;
    color: #6b7280;
    font-size: 11px;
    padding: 15px;
}}

@media print {{

    body {{
        background: white;
    }}

    .container {{
        max-width: none;
        padding: 0;
    }}

    .section,
    .header {{
        box-shadow: none;
        break-inside: avoid;
    }}

}}

</style>
</head>

<body>

<div class="container">

<div class="header">

    <h1>ORCA SAR MISSION BRIEF</h1>

    <p>
        Search and Rescue Operational Package
    </p>

    <span class="status">
        {escape(status)}
    </span>

</div>


<div class="section">

    <h2>1. Incident</h2>

    {build_incident_section(incident)}

</div>


<div class="section">

    <h2>2. Prioritized SAR Search Zones</h2>

    <table>

        <thead>
            <tr>
                <th>#</th>
                <th>Zone ID</th>
                <th>Probability</th>
                <th>Risk Score</th>
                <th>Priority</th>
                <th>Recommended Action</th>
            </tr>
        </thead>

        <tbody>
            {zone_rows}
        </tbody>

    </table>

</div>


<div class="section">

    <h2>3. Rescue Facility</h2>

    {build_rescue_section(rescue_facility)}

</div>


<div class="section">

    <h2>4. Rescue Route</h2>

    {build_route_section(rescue_route)}

</div>


<div class="section">

    <h2>5. Rescue Route Hazard Check</h2>

    {build_hazard_section(hazard_check)}

</div>


<div class="section">

    <h2>6. SAR Evidence</h2>

    <table>

        <thead>
            <tr>
                <th>Type</th>
                <th>Description</th>
                <th>Source</th>
                <th>Source Timestamp</th>
                <th>Confidence</th>
            </tr>
        </thead>

        <tbody>
            {evidence_rows}
        </tbody>

    </table>

</div>


<div class="section">

    <h2>7. Operational Warning</h2>

    <div class="warning">
        {escape(warning)}
    </div>

</div>


<div class="footer">

    ORCA SAR Mission Brief<br>
    Generated: {escape(generated_at)}<br>
    Operational planning artifact — verify field conditions
    before deployment.

</div>

</div>

</body>
</html>
"""


def main():
    incident_id = DEFAULT_INCIDENT_ID
    output_file = DEFAULT_OUTPUT

    if len(sys.argv) >= 2:
        incident_id = int(sys.argv[1])

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]

    print()
    print("ORCA SAR MISSION BRIEF")
    print()
    print(f"Incident ID : {incident_id}")
    print("Fetching mission package...")

    package = fetch_mission_package(
        incident_id
    )

    html = build_html(package)

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(html)

    print()
    print("MISSION BRIEF CREATED")
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


if __name__ == "__main__":
    main()