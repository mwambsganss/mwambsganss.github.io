#!/usr/bin/env python3
"""
Design Thinking Workshop Artifacts Generator
Generates all 17 artifacts from workshop transcript
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
import random
import math

# Lilly Brand Colors (approximations)
LILLY_RED = RGBColor(227, 24, 55)
LILLY_BLUE = RGBColor(0, 122, 194)
LILLY_GRAY = RGBColor(88, 89, 91)
LILLY_LIGHT_GRAY = RGBColor(200, 200, 200)

# IBM EDT-style colors for sticky notes
YELLOW = RGBColor(255, 242, 117)
PINK = RGBColor(255, 182, 193)
ORANGE = RGBColor(255, 160, 122)
GREEN = RGBColor(152, 251, 152)
BLUE = RGBColor(173, 216, 230)
TEAL = RGBColor(64, 224, 208)
RED = RGBColor(255, 105, 97)
GRAY = RGBColor(211, 211, 211)

# Background colors
KRAFT_BG = RGBColor(222, 184, 135)
WHITE_BG = RGBColor(255, 255, 255)

def add_title_slide(prs, title, subtitle=""):
    """Add a title slide with Lilly branding"""
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # Blank layout

    # Dark header bar
    header = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        0, 0, prs.slide_width, Inches(1.5)
    )
    header.fill.solid()
    header.fill.fore_color.rgb = LILLY_RED
    header.line.fill.background()

    # Title text
    title_box = slide.shapes.add_textbox(
        Inches(0.5), Inches(0.3),
        prs.slide_width - Inches(1), Inches(0.9)
    )
    title_frame = title_box.text_frame
    title_frame.text = title
    title_frame.paragraphs[0].font.size = Pt(44)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

    # Subtitle
    if subtitle:
        subtitle_box = slide.shapes.add_textbox(
            Inches(0.5), Inches(1.8),
            prs.slide_width - Inches(1), Inches(0.5)
        )
        subtitle_frame = subtitle_box.text_frame
        subtitle_frame.text = subtitle
        subtitle_frame.paragraphs[0].font.size = Pt(18)
        subtitle_frame.paragraphs[0].font.color.rgb = LILLY_GRAY

    return slide

def add_sticky_note(slide, left, top, width, height, text, color, rotation=0):
    """Add a sticky note shape with text"""
    note = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        left, top, width, height
    )
    note.fill.solid()
    note.fill.fore_color.rgb = color
    note.line.color.rgb = RGBColor(180, 180, 180)
    note.line.width = Pt(1)

    # Add slight rotation (in degrees * 60000)
    if rotation != 0:
        note.rotation = rotation

    # Add text
    text_frame = note.text_frame
    text_frame.text = text
    text_frame.word_wrap = True
    text_frame.margin_left = Inches(0.1)
    text_frame.margin_right = Inches(0.1)
    text_frame.margin_top = Inches(0.1)
    text_frame.margin_bottom = Inches(0.1)

    # Font styling
    for paragraph in text_frame.paragraphs:
        paragraph.font.size = Pt(11)
        paragraph.font.name = "Comic Sans MS"  # Hand-written style alternative
        paragraph.font.color.rgb = RGBColor(0, 0, 0)

    return note

def add_background(slide, prs, color=KRAFT_BG):
    """Add background color to slide"""
    background = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        0, 0, prs.slide_width, prs.slide_height
    )
    slide.shapes._spTree.remove(background._element)
    slide.shapes._spTree.insert(2, background._element)
    background.fill.solid()
    background.fill.fore_color.rgb = color
    background.line.fill.background()

def create_hopes_fears_board():
    """OUTPUT 1: Hopes & Fears Board"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(4), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Hopes & Fears"
    title_frame.paragraphs[0].font.size = Pt(48)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)

    # Section labels
    hopes_label = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(3), Inches(0.6))
    hopes_frame = hopes_label.text_frame
    hopes_frame.text = "HOPES"
    hopes_frame.paragraphs[0].font.size = Pt(36)
    hopes_frame.paragraphs[0].font.bold = True
    hopes_frame.paragraphs[0].font.color.rgb = RGBColor(0, 100, 0)

    fears_label = slide.shapes.add_textbox(Inches(0.5), Inches(5.2), Inches(3), Inches(0.6))
    fears_frame = fears_label.text_frame
    fears_frame.text = "FEARS"
    fears_frame.paragraphs[0].font.size = Pt(36)
    fears_frame.paragraphs[0].font.bold = True
    fears_frame.paragraphs[0].font.color.rgb = RGBColor(139, 0, 0)

    # Divider line
    line = slide.shapes.add_connector(1, Inches(0.5), Inches(5), Inches(15.5), Inches(5))
    line.line.width = Pt(3)
    line.line.color.rgb = RGBColor(0, 0, 0)

    # HOPES - Extract from transcript
    hopes = [
        "ADCO/MCOs: Visibility on the hand offs, so we can jump in and help/assist to keep/manage to the speed of the hand offs",
        "The quicker we get this info to Media parters the quicker they can work to get banners in market",
        "Standardization across lines of business, and business units",
        "Role clarity among everyone involved in the process",
        "Better systems in place that talk to each other",
        "Clear ownership of Creative Grid process within Lilly",
        "Revamp QA process before sent to agency",
        "Establishing Clear, End-to-End DTC Production Timeframes",
        "Consistency in approval process timing"
    ]

    # Place HOPES sticky notes
    x_positions = [1, 4, 7, 10, 13, 1, 4, 7, 10]
    y_positions = [2, 2.2, 2.1, 2, 2.2, 3.5, 3.6, 3.4, 3.5]
    colors = [YELLOW, GREEN, YELLOW, GREEN, YELLOW, GREEN, YELLOW, GREEN, YELLOW]
    rotations = [-2, 3, -1, 2, -3, 1, -2, 2, -1]

    for i, hope in enumerate(hopes):
        if i < len(x_positions):
            add_sticky_note(
                slide,
                Inches(x_positions[i]), Inches(y_positions[i]),
                Inches(2.5), Inches(1.2),
                hope, colors[i], rotations[i]
            )

    # FEARS - Extract from transcript
    fears = [
        "There are so many roles in this organization that constantly keep changing, its impossible to keep up",
        "A lot of black boxes folks don't quite understand who is supposed to be doing what",
        "There is area of improvement within the overall trafficking process to help cut down revisions and swirl",
        "There are sometimes too many cooks in the kitchen for the trafficking process",
        "Roles are not clearly owned",
        "The Lilly Digital team will traffic assets too quickly before a marketer sends an email",
        "There are a lot of handoffs with this new process that can make me feel frustrated",
        "I feel a loss of control when it gets to the creative grid process",
        "There is no clear standard on who should be filling out the grids, who is trafficking",
        "The number of handoffs in this process can feel heavy and sometimes frustrating"
    ]

    # Place FEARS sticky notes
    x_positions_fears = [1, 4, 7, 10, 13, 1, 4, 7, 10, 13]
    y_positions_fears = [6, 6.1, 6.2, 6, 6.1, 7.4, 7.5, 7.3, 7.4, 7.5]
    colors_fears = [PINK, ORANGE, PINK, ORANGE, PINK, ORANGE, PINK, ORANGE, PINK, ORANGE]
    rotations_fears = [2, -3, 1, -2, 3, -1, 2, -3, 1, -2]

    for i, fear in enumerate(fears):
        if i < len(x_positions_fears):
            add_sticky_note(
                slide,
                Inches(x_positions_fears[i]), Inches(y_positions_fears[i]),
                Inches(2.5), Inches(1),
                fear, colors_fears[i], rotations_fears[i]
            )

    prs.save('/Users/V5X8512/Downloads/01_hopes_fears.pptx')
    print("✓ Generated: 01_hopes_fears.pptx")

def create_personas():
    """OUTPUT 2: Personas"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    # Define personas from transcript
    personas = [
        {
            "name": "Mia (HCP Marketer)",
            "role": "HCP Marketing Lead",
            "quote": "I feel like there are a lot of handoffs with this new process that can make me feel frustrated or wish that it could be a click of a button",
            "goals": ["Kick off banners with brand strategy", "Project manage through MLR", "Be proactive 1-2 months out to ensure right message gets into market", "Think through the HCP experience"],
            "pains": ["A lot of handoffs in the process", "Takes 5-10 minutes to enter marketing inputs and that is hard to come by", "Loss of control in creative grid process", "Communication gaps - banners left hanging"],
            "behaviors": ["Presents idea to LMS or E2E colleagues", "Takes through MLR for approval", "Sends CMI team updated excel grid with banner rotation", "Fills in rotation, start, end date", "Checks in via email, Teams, or live during NPP weekly status"],
            "tools": ["MLR", "Excel/Creative Grid", "Email", "Teams", "NPP weekly status meetings"]
        },
        {
            "name": "Julie (DTC Media Lead)",
            "role": "DTC Media Strategy",
            "quote": "We need to work more strongly with the Lilly organization to understand impact when assets are not available and how that dilutes our marketplace impact",
            "goals": ["Ensure placements are strategically placed for patients/consumers", "Coordinate timing for market impact", "Drive scripts through targeted messaging"],
            "pains": ["Constant moving pieces", "Assets delayed or not available", "Negatively impacts the way plans drive action", "Dilutes marketplace impact"],
            "behaviors": ["Strategically determine placements for ad unit types", "Provide specs to TA & GCO CC&A team", "Confirm creative grid inputs are accurate", "Approve for agency hand off"],
            "tools": ["Media planning tools", "Creative grid", "Google Studio"]
        },
        {
            "name": "Jenn (HCP Agency - CMI)",
            "role": "Agency Media Operations",
            "quote": "CMI often has to help facilitate the task to see it through to completion in a timely manner to not delay launch",
            "goals": ["Receive and QA assets properly", "Build and launch media accurately", "Meet launch timelines"],
            "pains": ["Too many cooks in the kitchen", "Roles not clearly owned", "Click tags often missing", "Expiration dates not updated", "CMI often dark in the process"],
            "behaviors": ["Receive assets from Lilly through Google Studio or SharePoint", "QA assets for web specs & creative grids", "Assign creatives in internal systems", "Build tags and send to suppliers", "QA post launch"],
            "tools": ["Google Studio", "SharePoint", "Internal creative systems", "Ad serving platforms"]
        },
        {
            "name": "Matt (Digital Brand Lead)",
            "role": "Digital Development Strategy",
            "quote": "There is no clear standard on who should be filling out the grids, who is trafficking, and who is fixing failed creatives",
            "goals": ["Ensure assets delivered/trafficked on time", "Validate creatives prior to trafficking", "Remove blocks and escalate issues", "Discover innovation opportunities"],
            "pains": ["No clear standard on responsibilities", "Pulled in when information is missing", "Pulled in when QA fails", "Unclear who fixes failed creatives"],
            "behaviors": ["Partners with brands on digital development best practices", "Consults on digital tactic design for compliance", "Oversees QA to validate creatives", "Acts as escalation point"],
            "tools": ["Adobe Workfront (proposed)", "Creative trafficking forms", "QA systems"]
        },
        {
            "name": "Kate (Campaign Execution)",
            "role": "Campaign Activation Strategy",
            "quote": "There are many hands in the pot for this process. Order of operations is not clear. Roles and Responsibilities are fuzzy",
            "goals": ["Work with brand and omnichannel to determine banner needs", "Program banners in campaign software when approved"],
            "pains": ["Many hands in the pot", "Order of operations unclear", "Roles and responsibilities fuzzy", "Combination creates delays"],
            "behaviors": ["Receive/assess media plan", "Determine if banners need to be created", "Alert marketing and brand DCO to include in backlog", "Enter metadata in CAP"],
            "tools": ["CAP (Campaign Activation Platform)", "Media plans", "Backlog systems"]
        },
        {
            "name": "Molly (Media Operations)",
            "role": "Media Ops Process Owner",
            "quote": "There are so many roles in this organization that constantly keep changing, its impossible to keep up with how its changing",
            "goals": ["Ensure trafficking handoff processes work well", "Provide necessary tools like Smartsheet", "Enable teams to work together confidently"],
            "pains": ["Roles constantly changing", "Black boxes - unclear who does what", "When problems arise, hard to know who to triage"],
            "behaviors": ["Provides process documentation", "Manages Smartsheet tools", "Facilitates communication between groups"],
            "tools": ["Smartsheet", "Process documentation", "Communication platforms"]
        }
    ]

    for persona in personas:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        add_background(slide, prs, KRAFT_BG)

        # Persona name and role
        name_box = slide.shapes.add_textbox(Inches(2), Inches(0.5), Inches(12), Inches(0.6))
        name_frame = name_box.text_frame
        name_frame.text = persona["name"]
        name_frame.paragraphs[0].font.size = Pt(40)
        name_frame.paragraphs[0].font.bold = True
        name_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)

        role_box = slide.shapes.add_textbox(Inches(2), Inches(1.1), Inches(12), Inches(0.4))
        role_frame = role_box.text_frame
        role_frame.text = persona["role"]
        role_frame.paragraphs[0].font.size = Pt(20)
        role_frame.paragraphs[0].font.italic = True
        role_frame.paragraphs[0].font.color.rgb = LILLY_GRAY

        # Avatar placeholder
        avatar = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(0.5), Inches(0.5),
            Inches(1.2), Inches(1.2)
        )
        avatar.fill.solid()
        avatar.fill.fore_color.rgb = LILLY_LIGHT_GRAY
        avatar.line.color.rgb = LILLY_GRAY

        # Quote
        quote_box = slide.shapes.add_textbox(Inches(2), Inches(1.7), Inches(13), Inches(0.8))
        quote_frame = quote_box.text_frame
        quote_frame.text = f'"{persona["quote"]}"'
        quote_frame.paragraphs[0].font.size = Pt(14)
        quote_frame.paragraphs[0].font.italic = True
        quote_frame.paragraphs[0].font.color.rgb = RGBColor(80, 80, 80)

        # Goals section
        y_offset = 2.8
        label = slide.shapes.add_textbox(Inches(0.5), Inches(y_offset), Inches(3), Inches(0.3))
        label.text_frame.text = "GOALS & MOTIVATIONS"
        label.text_frame.paragraphs[0].font.size = Pt(14)
        label.text_frame.paragraphs[0].font.bold = True

        for i, goal in enumerate(persona["goals"][:3]):
            add_sticky_note(
                slide,
                Inches(0.5 + (i * 3.2)), Inches(y_offset + 0.4),
                Inches(3), Inches(0.8),
                goal, YELLOW, random.randint(-2, 2)
            )

        # Pain points section
        y_offset = 4.2
        label = slide.shapes.add_textbox(Inches(0.5), Inches(y_offset), Inches(3), Inches(0.3))
        label.text_frame.text = "PAIN POINTS"
        label.text_frame.paragraphs[0].font.size = Pt(14)
        label.text_frame.paragraphs[0].font.bold = True
        label.text_frame.paragraphs[0].font.color.rgb = RGBColor(139, 0, 0)

        for i, pain in enumerate(persona["pains"][:3]):
            add_sticky_note(
                slide,
                Inches(0.5 + (i * 3.2)), Inches(y_offset + 0.4),
                Inches(3), Inches(0.8),
                pain, PINK, random.randint(-2, 2)
            )

        # Behaviors section
        y_offset = 5.6
        label = slide.shapes.add_textbox(Inches(0.5), Inches(y_offset), Inches(3), Inches(0.3))
        label.text_frame.text = "KEY BEHAVIORS"
        label.text_frame.paragraphs[0].font.size = Pt(14)
        label.text_frame.paragraphs[0].font.bold = True

        for i, behavior in enumerate(persona["behaviors"][:3]):
            add_sticky_note(
                slide,
                Inches(0.5 + (i * 3.2)), Inches(y_offset + 0.4),
                Inches(3), Inches(0.8),
                behavior, BLUE, random.randint(-2, 2)
            )

        # Tools section
        y_offset = 7
        label = slide.shapes.add_textbox(Inches(0.5), Inches(y_offset), Inches(3), Inches(0.3))
        label.text_frame.text = "TOOLS & SYSTEMS"
        label.text_frame.paragraphs[0].font.size = Pt(14)
        label.text_frame.paragraphs[0].font.bold = True

        for i, tool in enumerate(persona["tools"][:3]):
            add_sticky_note(
                slide,
                Inches(0.5 + (i * 3.2)), Inches(y_offset + 0.4),
                Inches(3), Inches(0.6),
                tool, GREEN, random.randint(-2, 2)
            )

    prs.save('/Users/V5X8512/Downloads/02_personas.pptx')
    print("✓ Generated: 02_personas.pptx")

def create_stakeholder_map():
    """OUTPUT 3: Stakeholder Map"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(6), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Stakeholder Map"
    title_frame.paragraphs[0].font.size = Pt(48)
    title_frame.paragraphs[0].font.bold = True

    # Central initiative
    center = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(6.5), Inches(3.5),
        Inches(3), Inches(2)
    )
    center.fill.solid()
    center.fill.fore_color.rgb = LILLY_RED
    center.line.color.rgb = RGBColor(0, 0, 0)
    center.line.width = Pt(2)

    center_text = center.text_frame
    center_text.text = "Banner Display\nTrafficking &\nHandoff Process"
    center_text.paragraphs[0].alignment = PP_ALIGN.CENTER
    center_text.vertical_anchor = MSO_ANCHOR.MIDDLE
    for paragraph in center_text.paragraphs:
        paragraph.font.size = Pt(18)
        paragraph.font.bold = True
        paragraph.font.color.rgb = RGBColor(255, 255, 255)

    # Stakeholder groups with verbatim quotes
    stakeholders = [
        {
            "group": "ADCO/MCO",
            "role": "Carrie Sieglitz",
            "quote": "We tend to be the one asked where is the banner at the end or why doesn't CMI have the files",
            "position": (1, 1.5),
            "color": YELLOW
        },
        {
            "group": "Marketers (HCP)",
            "role": "Mia Lynn McCrumb",
            "quote": "I have to be proactive (think 1-2 months out) to ensure the right message gets into market",
            "position": (1, 4.5),
            "color": YELLOW
        },
        {
            "group": "Marketers (DTC)",
            "role": "Jamie Doyle",
            "quote": "The DTC marketer should own the media grid so that the marketer is very in the loop",
            "position": (1, 7),
            "color": YELLOW
        },
        {
            "group": "Media Leads",
            "role": "Julie Gogan, Alex Lund",
            "quote": "We need to work more strongly with the Lilly organization to understand impact when assets are not available",
            "position": (4.5, 1),
            "color": BLUE
        },
        {
            "group": "Media Operations",
            "role": "Molly Hudlow",
            "quote": "There are so many roles that constantly keep changing, its impossible to keep up",
            "position": (11, 1),
            "color": BLUE
        },
        {
            "group": "HCP Agency (CMI)",
            "role": "Jenn Margiloff",
            "quote": "CMI often has to help facilitate the task to see it through to completion in a timely manner",
            "position": (13, 3.5),
            "color": GREEN
        },
        {
            "group": "Consumer Agency (PA)",
            "role": "Alex Fox",
            "quote": "Better learning and understanding of processes between teams to aid in collaboration",
            "position": (13, 6.5),
            "color": GREEN
        },
        {
            "group": "Digital Brand Lead",
            "role": "Matt Casolaro",
            "quote": "There is no clear standard on who should be filling out the grids, who is trafficking",
            "position": (11, 7.5),
            "color": ORANGE
        },
        {
            "group": "Campaign Execution",
            "role": "Kate Kilgore",
            "quote": "There are many hands in the pot. Order of operations is not clear",
            "position": (4.5, 7.5),
            "color": ORANGE
        },
        {
            "group": "Digital PM/Production",
            "role": "LMS, E2E Team",
            "quote": "Intakes creative requests, production in platform, trafficking and handoff to agencies",
            "position": (8, 7.5),
            "color": TEAL
        }
    ]

    for stakeholder in stakeholders:
        # Role sticky note
        add_sticky_note(
            slide,
            Inches(stakeholder["position"][0]), Inches(stakeholder["position"][1]),
            Inches(2.2), Inches(0.5),
            f"{stakeholder['group']}\n{stakeholder['role']}",
            stakeholder["color"], random.randint(-3, 3)
        )

        # Quote sticky note below
        add_sticky_note(
            slide,
            Inches(stakeholder["position"][0]), Inches(stakeholder["position"][1] + 0.6),
            Inches(2.2), Inches(0.8),
            f'"{stakeholder["quote"]}"',
            RGBColor(255, 255, 220), random.randint(-2, 2)
        )

    prs.save('/Users/V5X8512/Downloads/03_stakeholder_map.pptx')
    print("✓ Generated: 03_stakeholder_map.pptx")

# Run all generation functions
if __name__ == "__main__":
    print("Generating Design Thinking Workshop Artifacts...")
    print("=" * 60)

    create_hopes_fears_board()
    create_personas()
    create_stakeholder_map()

    print("=" * 60)
    print("Completed first 3 artifacts. Continuing with remaining outputs...")
