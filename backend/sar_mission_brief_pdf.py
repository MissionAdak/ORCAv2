from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from pathlib import Path


OUTPUT_FILE = "sar_mission_brief.pdf"


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    heading_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=8,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=5,
    )

    small_style = ParagraphStyle(
        "SmallCustom",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
    )

    story = []

    # ---------------------------------------------------------
    # TITLE
    # ---------------------------------------------------------

    story.append(Paragraph("SAR MISSION BRIEF", title_style))

    story.append(
        Paragraph(
            "Search and Rescue Mission Operations Brief",
            ParagraphStyle(
                "Subtitle",
                parent=normal_style,
                alignment=TA_CENTER,
                fontSize=10,
                spaceAfter=15,
            ),
        )
    )

    # ---------------------------------------------------------
    # 1. MISSION OVERVIEW
    # ---------------------------------------------------------

    story.append(Paragraph("1. Mission Overview", heading_style))

    story.append(
        Paragraph(
            "This mission brief provides a structured overview of a Search and Rescue "
            "(SAR) operation. It is designed to help the operations team quickly "
            "understand the incident, available information, risks, resources, and "
            "recommended actions.",
            normal_style,
        )
    )

    # ---------------------------------------------------------
    # 2. INCIDENT INFORMATION
    # ---------------------------------------------------------

    story.append(Paragraph("2. Incident Information", heading_style))

    incident_data = [
        ["Field", "Information"],
        ["Mission Type", "Search and Rescue"],
        ["Status", "Active"],
        ["Priority", "High"],
        ["Location", "Marine / Coastal Area"],
        ["Incident Source", "Operational Alert"],
        [
            "Primary Objective",
            "Locate and assist persons or vessels in distress",
        ],
    ]

    incident_table = Table(
        incident_data,
        colWidths=[45 * mm, 125 * mm],
    )

    incident_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 11),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(incident_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # 3. ENVIRONMENTAL CONDITIONS
    # ---------------------------------------------------------

    story.append(Paragraph("3. Environmental Conditions", heading_style))

    environment_data = [
        ["Parameter", "Value", "Risk / Observation"],
        ["Wave Height", "1.4 m", "Moderate sea condition"],
        ["Wind Speed", "18 km/h", "Monitor continuously"],
        ["Fishing Zone", "14 km offshore", "Relevant activity area"],
        ["Overall Risk", "MODERATE", "Operational caution required"],
    ]

    env_table = Table(
        environment_data,
        colWidths=[45 * mm, 35 * mm, 90 * mm],
    )

    env_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    story.append(env_table)
    story.append(Spacer(1, 8))

    # ---------------------------------------------------------
    # 4. RISK ASSESSMENT
    # ---------------------------------------------------------

    story.append(Paragraph("4. Risk Assessment", heading_style))

    story.append(
        Paragraph(
            "<b>Risk Level: MODERATE</b><br/>"
            "Current environmental information indicates moderate operational risk. "
            "Teams should continuously monitor wind, wave conditions, vessel movement, "
            "and any new intelligence received during the mission.",
            normal_style,
        )
    )

    # ---------------------------------------------------------
    # 5. MISSION OBJECTIVES
    # ---------------------------------------------------------

    story.append(Paragraph("5. Mission Objectives", heading_style))

    objectives = [
        "Identify the probable location of the person or vessel in distress.",
        "Collect and verify available incident information.",
        "Monitor environmental and marine conditions.",
        "Coordinate search resources and response teams.",
        "Maintain communication with all participating units.",
        "Record evidence and operational updates.",
        "Provide assistance once the target is located.",
    ]

    for i, objective in enumerate(objectives, 1):
        story.append(
            Paragraph(
                f"{i}. {objective}",
                normal_style,
            )
        )

    # ---------------------------------------------------------
    # 6. AVAILABLE EVIDENCE
    # ---------------------------------------------------------

    evidence_data = [
        ["Evidence Source", "Status"],
        ["Incident Information", "Available"],
        ["Environmental Data", "Available"],
        ["Marine Map", "Available"],
        ["Operational Updates", "Live / To be monitored"],
    ]

    evidence_table = Table(
        evidence_data,
        colWidths=[90 * mm, 80 * mm],
    )

    evidence_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#374151")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )

    # Keep heading + table together
    story.append(
        KeepTogether(
            [
                Paragraph("6. Available Evidence", heading_style),
                evidence_table,
                Spacer(1, 8),
            ]
        )
    )

    # ---------------------------------------------------------
    # 7. RECOMMENDED OPERATIONAL ACTIONS
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "7. Recommended Operational Actions",
            heading_style,
        )
    )

    actions = [
        "Review the latest incident information before deployment.",
        "Check the marine map and identify the relevant search area.",
        "Monitor weather and sea conditions throughout the operation.",
        "Coordinate search units through the command center.",
        "Keep an updated record of observations and evidence.",
        "Escalate the mission if environmental or operational risk increases.",
    ]

    for action in actions:
        story.append(
            Paragraph(
                "• " + action,
                normal_style,
            )
        )

    # ---------------------------------------------------------
    # 8. COMMAND CENTER
    # ---------------------------------------------------------

    story.append(Paragraph("8. Command Center", heading_style))

    story.append(
        Paragraph(
            "The Command Center provides a centralized operational view containing "
            "the active mission panel, marine map, evidence, environmental information, "
            "and mission status. Operators can use this information to coordinate "
            "response activities and maintain situational awareness.",
            normal_style,
        )
    )

    # ---------------------------------------------------------
    # 9. MISSION STATUS
    # ---------------------------------------------------------

    story.append(Paragraph("9. Mission Status", heading_style))

    status_data = [
        ["Component", "Status"],
        ["Mission", "ACTIVE"],
        ["Risk", "MODERATE"],
        ["Wave", "1.4 m"],
        ["Wind", "18 km/h"],
        ["PFZ", "14 km offshore"],
        ["Evidence", "Available"],
        ["Map", "Available"],
    ]

    status_table = Table(
        status_data,
        colWidths=[80 * mm, 90 * mm],
    )

    status_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(status_table)
    story.append(Spacer(1, 12))

    # ---------------------------------------------------------
    # FOOTER
    # ---------------------------------------------------------

    story.append(
        Paragraph(
            "Generated by ORCA Mission Operations System",
            ParagraphStyle(
                "Footer",
                parent=small_style,
                alignment=TA_CENTER,
            ),
        )
    )

    # Build PDF
    doc.build(story)


if __name__ == "__main__":
    build_pdf()
    print(
        f"PDF created successfully: {Path(OUTPUT_FILE).resolve()}"
    )