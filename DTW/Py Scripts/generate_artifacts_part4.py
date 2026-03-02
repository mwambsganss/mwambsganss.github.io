#!/usr/bin/env python3
"""
Design Thinking Workshop Artifacts Generator - Part 4
Experience Roadmap, Hills, Gantt Roadmap, Resource Plan
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import random

# Color definitions
LILLY_RED = RGBColor(227, 24, 55)
LILLY_BLUE = RGBColor(0, 122, 194)
LILLY_GRAY = RGBColor(88, 89, 91)
YELLOW = RGBColor(255, 242, 117)
PINK = RGBColor(255, 182, 193)
ORANGE = RGBColor(255, 160, 122)
GREEN = RGBColor(152, 251, 152)
BLUE = RGBColor(173, 216, 230)
TEAL = RGBColor(64, 224, 208)
RED = RGBColor(255, 105, 97)
KRAFT_BG = RGBColor(222, 184, 135)
WHITE_BG = RGBColor(255, 255, 255)

def add_background(slide, prs, color):
    background = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    slide.shapes._spTree.remove(background._element)
    slide.shapes._spTree.insert(2, background._element)
    background.fill.solid()
    background.fill.fore_color.rgb = color
    background.line.fill.background()

def add_sticky_note(slide, left, top, width, height, text, color, rotation=0):
    note = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    note.fill.solid()
    note.fill.fore_color.rgb = color
    note.line.color.rgb = RGBColor(180, 180, 180)
    note.line.width = Pt(1)
    if rotation != 0:
        note.rotation = rotation
    text_frame = note.text_frame
    text_frame.text = text
    text_frame.word_wrap = True
    text_frame.margin_left = Inches(0.1)
    text_frame.margin_right = Inches(0.1)
    text_frame.margin_top = Inches(0.1)
    text_frame.margin_bottom = Inches(0.1)
    for paragraph in text_frame.paragraphs:
        paragraph.font.size = Pt(10)
        paragraph.font.name = "Comic Sans MS"
        paragraph.font.color.rgb = RGBColor(0, 0, 0)
    return note

def create_experience_roadmap():
    """OUTPUT 11: Experience-Based Roadmap"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, KRAFT_BG)

    # Header
    header_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(15), Inches(0.6))
    header_frame = header_box.text_frame
    header_frame.text = "OUR USER CAN / OUR USER WILL BE ABLE TO..."
    header_frame.paragraphs[0].font.size = Pt(36)
    header_frame.paragraphs[0].font.bold = True
    header_frame.paragraphs[0].font.color.rgb = LILLY_RED
    header_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Column headers
    columns = ["NEAR-TERM (Months 1-3)\nCupcake", "MID-TERM (Months 4-6)\nBirthday Cake", "LONG-TERM (Months 7-12)\nWedding Cake"]
    col_x = [1, 6, 11]

    for i, col in enumerate(columns):
        col_box = slide.shapes.add_textbox(Inches(col_x[i]), Inches(1.2), Inches(4.5), Inches(0.6))
        col_frame = col_box.text_frame
        col_frame.text = col
        col_frame.paragraphs[0].font.size = Pt(16)
        col_frame.paragraphs[0].font.bold = True
        col_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Vertical dividers
    for x in [5.5, 10.5]:
        divider = slide.shapes.add_connector(2, Inches(x), Inches(1.8), Inches(x), Inches(8.5))
        divider.line.width = Pt(2)
        divider.line.color.rgb = RGBColor(100, 100, 100)

    # Near-term capabilities
    near_term = [
        "Our user can see clear roles and responsibilities for each step",
        "Our user can access a marketer cheat sheet with required steps",
        "Our user can receive Teams channel notifications when handoffs are ready",
        "Our user can view a quarterly rotation matrix aligned with creative grid",
        "Our user can track banner status (Not Started → In Progress → Ready → Launched)",
        "Our marketer can complete grid inputs in under 2 minutes with pre-filled fields"
    ]

    y = 2
    for item in near_term:
        add_sticky_note(slide, Inches(1), Inches(y), Inches(4.2), Inches(0.9), item, YELLOW, random.randint(-2, 2))
        y += 1

    # Mid-term capabilities
    mid_term = [
        "⭐ Our user can benefit from automated grid notifications when steps complete",
        "Our user can access a high-level creative map showing what launches when and why",
        "⭐ Our user can leverage auto-populated metadata in the creative grid",
        "Our agency can receive assets with complete and accurate information in one handoff",
        "Our user can utilize standardized banner templates across HCP and DTC",
        "Our user can see one day turnaround from AFD to CMI QA"
    ]

    y = 2
    for item in mid_term:
        add_sticky_note(slide, Inches(6), Inches(y), Inches(4.2), Inches(0.9), item, GREEN, random.randint(-2, 2))
        y += 1

    # Long-term capabilities
    long_term = [
        "⭐ Our user can benefit from fully automated metadata collection and grid population",
        "Our user can work in a unified workflow system with Adobe Workfront integration",
        "Our user can leverage a fast-track path for high-urgency messages with pre-approved templates",
        "⭐ Our user can experience seamless system integration where tools talk to each other",
        "Our marketer can feel confident banners reach market without communication gaps",
        "Our organization can achieve standardization across all business units and lines"
    ]

    y = 2
    for item in long_term:
        add_sticky_note(slide, Inches(11), Inches(y), Inches(4.2), Inches(0.9), item, TEAL, random.randint(-2, 2))
        y += 1

    # Legend
    legend_box = slide.shapes.add_textbox(Inches(0.5), Inches(8.3), Inches(8), Inches(0.4))
    legend_frame = legend_box.text_frame
    legend_frame.text = "⭐ = Automation/Agentic Capability"
    legend_frame.paragraphs[0].font.size = Pt(12)
    legend_frame.paragraphs[0].font.color.rgb = LILLY_BLUE

    prs.save('/Users/V5X8512/Downloads/11_experience_roadmap.pptx')
    print("✓ Generated: 11_experience_roadmap.pptx")

def create_hills():
    """OUTPUT 12: Hills / Objectives"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(6), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Hills"
    title_frame.paragraphs[0].font.size = Pt(48)
    title_frame.paragraphs[0].font.bold = True

    # Hills from transcript - synthesized from goals and roadmap
    hills = [
        {
            "who": "Marketers and Media Teams",
            "what": "Complete banner trafficking from AFD to live in market within 1 day with zero communication gaps",
            "wow": "Reducing time to market by 80% and eliminating all handoff-related delays"
        },
        {
            "who": "All trafficking process stakeholders",
            "what": "Know exactly who owns each step, what actions are required, and receive automated notifications when it's their turn",
            "wow": "Achieving 100% role clarity and eliminating all black box confusion across teams"
        },
        {
            "who": "HCP and Consumer Agencies",
            "what": "Receive complete, accurate, error-free banner assets with all required metadata in a single automated handoff",
            "wow": "Reducing agency QA rework by 90% and meeting SLA requirements consistently"
        }
    ]

    y_offset = 1.5
    for hill in hills:
        # Card background
        card = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(1), Inches(y_offset),
            Inches(14), Inches(1.8)
        )
        card.fill.solid()
        card.fill.fore_color.rgb = KRAFT_BG
        card.line.color.rgb = RGBColor(100, 100, 100)
        card.line.width = Pt(2)

        # Triangle icon
        icon_box = slide.shapes.add_textbox(Inches(1.3), Inches(y_offset + 0.1), Inches(0.5), Inches(0.5))
        icon_frame = icon_box.text_frame
        icon_frame.text = "▲"
        icon_frame.paragraphs[0].font.size = Pt(32)
        icon_frame.paragraphs[0].font.color.rgb = LILLY_RED

        # Hill text
        text_box = slide.shapes.add_textbox(Inches(2), Inches(y_offset + 0.2), Inches(12.5), Inches(1.4))
        text_frame = text_box.text_frame
        text_frame.word_wrap = True

        p1 = text_frame.paragraphs[0]
        p1.text = f"WHO: {hill['who']}"
        p1.font.size = Pt(12)
        p1.font.name = "Courier New"
        p1.level = 0

        p2 = text_frame.add_paragraph()
        p2.text = f"WHAT: {hill['what']}"
        p2.font.size = Pt(12)
        p2.font.name = "Courier New"
        p2.level = 0

        p3 = text_frame.add_paragraph()
        p3.text = f"WOW: {hill['wow']}"
        p3.font.size = Pt(12)
        p3.font.name = "Courier New"
        p3.font.bold = True
        p3.font.color.rgb = LILLY_RED
        p3.level = 0

        y_offset += 2.2

    prs.save('/Users/V5X8512/Downloads/12_hills.pptx')
    print("✓ Generated: 12_hills.pptx")

def create_gantt_roadmap():
    """OUTPUT 13: Gantt Roadmap"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(6), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Roadmap"
    title_frame.paragraphs[0].font.size = Pt(40)
    title_frame.paragraphs[0].font.bold = True

    # Timeline header (12 months)
    timeline_x = 4.5
    timeline_width = 10.5
    month_width = timeline_width / 12

    # Zone labels
    zones = [
        ("SHORT-TERM", 0, 3, YELLOW),
        ("MID-TERM", 3, 3, GREEN),
        ("LONG-TERM", 6, 6, BLUE)
    ]

    for zone_name, start_month, duration, color in zones:
        zone_box = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(timeline_x + start_month * month_width), Inches(0.9),
            Inches(duration * month_width), Inches(0.4)
        )
        zone_box.fill.solid()
        zone_box.fill.fore_color.rgb = color
        zone_box.line.fill.background()

        zone_text = zone_box.text_frame
        zone_text.text = zone_name
        zone_text.vertical_anchor = MSO_ANCHOR.MIDDLE
        zone_text.paragraphs[0].alignment = PP_ALIGN.CENTER
        zone_text.paragraphs[0].font.size = Pt(10)
        zone_text.paragraphs[0].font.bold = True

    # Month numbers
    for i in range(12):
        month_box = slide.shapes.add_textbox(
            Inches(timeline_x + i * month_width), Inches(1.35),
            Inches(month_width), Inches(0.25)
        )
        month_frame = month_box.text_frame
        month_frame.text = str(i + 1)
        month_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        month_frame.paragraphs[0].font.size = Pt(9)

    # Initiative groups and items
    initiatives = [
        {
            "theme": "QUICK WINS & AUTOMATION",
            "color": LILLY_RED,
            "items": [
                {"name": "⭐ Teams Channel Notifications", "start": 0, "duration": 1, "priority": True},
                {"name": "⭐ Automated Grid Notifications", "start": 0, "duration": 2, "priority": True},
                {"name": "Role Clarity Documentation (RACI)", "start": 0, "duration": 2, "priority": True},
                {"name": "Marketer Cheat Sheet", "start": 1, "duration": 1, "priority": False}
            ]
        },
        {
            "theme": "PROCESS & COMMUNICATION",
            "color": LILLY_BLUE,
            "items": [
                {"name": "Status Tracker Implementation", "start": 1, "duration": 2, "priority": False},
                {"name": "Quarterly Rotation Matrix Template", "start": 1, "duration": 2, "priority": False},
                {"name": "High-Level Creative Map", "start": 3, "duration": 2, "priority": False},
                {"name": "Enhanced QA Process", "start": 4, "duration": 2, "priority": False}
            ]
        },
        {
            "theme": "GRID & SYSTEMS IMPROVEMENT",
            "color": TEAL,
            "items": [
                {"name": "Creative Grid Simplification", "start": 2, "duration": 3, "priority": False},
                {"name": "⭐ Metadata Auto-Population", "start": 4, "duration": 4, "priority": True},
                {"name": "Workfront Integration", "start": 6, "duration": 4, "priority": False},
                {"name": "⭐ Full Grid Automation", "start": 8, "duration": 4, "priority": True}
            ]
        },
        {
            "theme": "STANDARDIZATION & SCALE",
            "color": LILLY_GRAY,
            "items": [
                {"name": "Fast-Track Templates", "start": 5, "duration": 3, "priority": False},
                {"name": "Cross-BU Standardization", "start": 7, "duration": 5, "priority": False},
                {"name": "⭐ Unified Workflow System", "start": 9, "duration": 3, "priority": True}
            ]
        }
    ]

    y_offset = 2
    for group in initiatives:
        # Theme header
        theme_box = slide.shapes.add_textbox(Inches(0.5), Inches(y_offset), Inches(3.8), Inches(0.3))
        theme_frame = theme_box.text_frame
        theme_frame.text = group["theme"]
        theme_frame.paragraphs[0].font.size = Pt(11)
        theme_frame.paragraphs[0].font.bold = True
        theme_frame.paragraphs[0].font.color.rgb = group["color"]

        y_offset += 0.35

        # Items
        for item in group["items"]:
            # Initiative name
            name_box = slide.shapes.add_textbox(Inches(0.5), Inches(y_offset), Inches(3.8), Inches(0.3))
            name_frame = name_box.text_frame
            name_frame.text = ("★ " if item["priority"] else "") + item["name"]
            name_frame.paragraphs[0].font.size = Pt(9)

            # Timeline bar
            bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE,
                Inches(timeline_x + item["start"] * month_width), Inches(y_offset),
                Inches(item["duration"] * month_width), Inches(0.25)
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = group["color"]
            bar.line.color.rgb = RGBColor(80, 80, 80)
            bar.line.width = Pt(1)

            y_offset += 0.35

        y_offset += 0.15

    # Legend
    legend_box = slide.shapes.add_textbox(Inches(0.5), Inches(8.2), Inches(8), Inches(0.5))
    legend_frame = legend_box.text_frame
    legend_frame.text = "★ = High Priority    ⭐ = Automation/Agentic Capability"
    legend_frame.paragraphs[0].font.size = Pt(10)

    prs.save('/Users/V5X8512/Downloads/13_roadmap.pptx')
    print("✓ Generated: 13_roadmap.pptx")

def create_resource_plan():
    """OUTPUT 14: Resource Plan"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(6), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Resource Plan"
    title_frame.paragraphs[0].font.size = Pt(40)
    title_frame.paragraphs[0].font.bold = True

    # Table header
    headers = ["Initiative", "Required Role/Skill", "Owner/Team", "Effort", "Dependencies", "Gap"]
    col_widths = [3, 2.5, 2, 1.2, 3, 1]
    col_x = 0.5

    # Draw header row
    y = 1
    for i, header in enumerate(headers):
        header_box = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(col_x), Inches(y),
            Inches(col_widths[i]), Inches(0.4)
        )
        header_box.fill.solid()
        header_box.fill.fore_color.rgb = LILLY_GRAY
        header_box.line.color.rgb = RGBColor(100, 100, 100)

        header_text = header_box.text_frame
        header_text.text = header
        header_text.vertical_anchor = MSO_ANCHOR.MIDDLE
        header_text.paragraphs[0].alignment = PP_ALIGN.CENTER
        header_text.paragraphs[0].font.size = Pt(10)
        header_text.paragraphs[0].font.bold = True
        header_text.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

        col_x += col_widths[i]

    # Table data
    resources = [
        {"initiative": "Teams Notifications", "role": "IT/Platform Admin", "owner": "Media Ops", "effort": "Low", "deps": "Teams setup", "gap": ""},
        {"initiative": "Automated Grid Notifications", "role": "Developer", "owner": "TBD", "effort": "Medium", "deps": "Smartsheet API access", "gap": "⚠"},
        {"initiative": "RACI Documentation", "role": "Process Owner", "owner": "Media Ops - Molly", "effort": "Low", "deps": "Stakeholder input", "gap": ""},
        {"initiative": "Marketer Cheat Sheet", "role": "Process Designer", "owner": "ADCO - Carrie", "effort": "Low", "deps": "RACI complete", "gap": ""},
        {"initiative": "Status Tracker", "role": "PM/Business Analyst", "owner": "TBD", "effort": "Medium", "deps": "Tool selection", "gap": "⚠"},
        {"initiative": "Quarterly Matrix Template", "role": "Marketing Ops", "owner": "Mia/Jamie", "effort": "Low", "deps": "Template design", "gap": ""},
        {"initiative": "Creative Grid Simplification", "role": "UX Designer + Developer", "owner": "TBD", "effort": "High", "deps": "User research", "gap": "⚠"},
        {"initiative": "Metadata Auto-Population", "role": "Developer + Data Analyst", "owner": "TBD", "effort": "High", "deps": "Source system integration", "gap": "⚠"},
        {"initiative": "Workfront Integration", "role": "Workfront Admin + Developer", "owner": "Digital PM Team", "effort": "High", "deps": "Workfront license", "gap": ""},
        {"initiative": "Cross-BU Standardization", "role": "Change Management", "owner": "TBD", "effort": "High", "deps": "Executive sponsorship", "gap": "⚠"}
    ]

    # Effort colors
    effort_colors = {"Low": GREEN, "Medium": YELLOW, "High": RED}

    y = 1.4
    for resource in resources:
        col_x = 0.5

        # Initiative
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(col_x), Inches(y), Inches(col_widths[0]), Inches(0.35))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE_BG if not resource["gap"] else ORANGE
        box.line.color.rgb = RGBColor(180, 180, 180)
        box.text_frame.text = resource["initiative"]
        box.text_frame.paragraphs[0].font.size = Pt(8)
        box.text_frame.margin_left = Inches(0.05)
        col_x += col_widths[0]

        # Role
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(col_x), Inches(y), Inches(col_widths[1]), Inches(0.35))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE_BG
        box.line.color.rgb = RGBColor(180, 180, 180)
        box.text_frame.text = resource["role"]
        box.text_frame.paragraphs[0].font.size = Pt(8)
        box.text_frame.margin_left = Inches(0.05)
        box.text_frame.word_wrap = True
        col_x += col_widths[1]

        # Owner
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(col_x), Inches(y), Inches(col_widths[2]), Inches(0.35))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE_BG
        box.line.color.rgb = RGBColor(180, 180, 180)
        box.text_frame.text = resource["owner"]
        box.text_frame.paragraphs[0].font.size = Pt(8)
        box.text_frame.margin_left = Inches(0.05)
        box.text_frame.word_wrap = True
        col_x += col_widths[2]

        # Effort
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(col_x), Inches(y), Inches(col_widths[3]), Inches(0.35))
        box.fill.solid()
        box.fill.fore_color.rgb = effort_colors[resource["effort"]]
        box.line.color.rgb = RGBColor(180, 180, 180)
        box.text_frame.text = resource["effort"]
        box.text_frame.paragraphs[0].font.size = Pt(8)
        box.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        box.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        col_x += col_widths[3]

        # Dependencies
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(col_x), Inches(y), Inches(col_widths[4]), Inches(0.35))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE_BG
        box.line.color.rgb = RGBColor(180, 180, 180)
        box.text_frame.text = resource["deps"]
        box.text_frame.paragraphs[0].font.size = Pt(8)
        box.text_frame.margin_left = Inches(0.05)
        box.text_frame.word_wrap = True
        col_x += col_widths[4]

        # Gap
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(col_x), Inches(y), Inches(col_widths[5]), Inches(0.35))
        box.fill.solid()
        box.fill.fore_color.rgb = WHITE_BG
        box.line.color.rgb = RGBColor(180, 180, 180)
        box.text_frame.text = resource["gap"]
        box.text_frame.paragraphs[0].font.size = Pt(12)
        box.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        box.text_frame.vertical_anchor = MSO_ANCHOR.MIDDLE

        y += 0.35

    # Legend
    legend_box = slide.shapes.add_textbox(Inches(0.5), Inches(8.2), Inches(10), Inches(0.4))
    legend_frame = legend_box.text_frame
    legend_frame.text = "⚠ = Unassigned/Gap    Effort Levels: Green=Low, Yellow=Medium, Red=High"
    legend_frame.paragraphs[0].font.size = Pt(10)

    prs.save('/Users/V5X8512/Downloads/14_resource_plan.pptx')
    print("✓ Generated: 14_resource_plan.pptx")

if __name__ == "__main__":
    print("Generating Artifacts 11-14...")
    print("=" * 60)

    create_experience_roadmap()
    create_hills()
    create_gantt_roadmap()
    create_resource_plan()

    print("=" * 60)
    print("Completed artifacts 11-14")
