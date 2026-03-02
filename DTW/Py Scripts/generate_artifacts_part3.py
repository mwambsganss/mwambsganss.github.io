#!/usr/bin/env python3
"""
Design Thinking Workshop Artifacts Generator - Part 3
Assumptions, Big Ideas, Prioritization, To-Be Map
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
GRAY = RGBColor(211, 211, 211)
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

def create_assumptions_grid():
    """OUTPUT 7: Assumptions and Questions 2x2 Grid"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, KRAFT_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(8), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Assumptions & Questions"
    title_frame.paragraphs[0].font.size = Pt(40)
    title_frame.paragraphs[0].font.bold = True

    # Draw 2x2 grid
    grid_left = 2
    grid_top = 1.5
    grid_width = 12
    grid_height = 6.5

    # Vertical axis
    v_axis = slide.shapes.add_connector(2, Inches(grid_left), Inches(grid_top), Inches(grid_left), Inches(grid_top + grid_height))
    v_axis.line.width = Pt(3)
    v_axis.line.color.rgb = RGBColor(0, 0, 0)

    # Horizontal axis
    h_axis = slide.shapes.add_connector(1, Inches(grid_left), Inches(grid_top + grid_height/2), Inches(grid_left + grid_width), Inches(grid_top + grid_height/2))
    h_axis.line.width = Pt(3)
    h_axis.line.color.rgb = RGBColor(0, 0, 0)

    # Axis labels
    # Vertical: HIGH RISK (top) to LOW RISK (bottom)
    high_risk_label = slide.shapes.add_textbox(Inches(0.5), Inches(grid_top), Inches(1.3), Inches(0.4))
    high_risk_label.text_frame.text = "HIGH\nRISK"
    high_risk_label.text_frame.paragraphs[0].font.size = Pt(12)
    high_risk_label.text_frame.paragraphs[0].font.bold = True
    high_risk_label.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    low_risk_label = slide.shapes.add_textbox(Inches(0.5), Inches(grid_top + grid_height - 0.5), Inches(1.3), Inches(0.4))
    low_risk_label.text_frame.text = "LOW\nRISK"
    low_risk_label.text_frame.paragraphs[0].font.size = Pt(12)
    low_risk_label.text_frame.paragraphs[0].font.bold = True
    low_risk_label.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Horizontal: CERTAIN (left) to UNCERTAIN (right)
    certain_label = slide.shapes.add_textbox(Inches(grid_left), Inches(grid_top + grid_height + 0.2), Inches(2), Inches(0.4))
    certain_label.text_frame.text = "CERTAIN"
    certain_label.text_frame.paragraphs[0].font.size = Pt(12)
    certain_label.text_frame.paragraphs[0].font.bold = True
    certain_label.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    uncertain_label = slide.shapes.add_textbox(Inches(grid_left + grid_width - 2), Inches(grid_top + grid_height + 0.2), Inches(2), Inches(0.4))
    uncertain_label.text_frame.text = "UNCERTAIN"
    uncertain_label.text_frame.paragraphs[0].font.size = Pt(12)
    uncertain_label.text_frame.paragraphs[0].font.bold = True
    uncertain_label.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Assumptions and questions from transcript
    items = [
        {
            "text": "I assume other roles know what the other role is doing in the process",
            "risk": "high", "certainty": "uncertain", "color": RED
        },
        {
            "text": "Do teams know who to ask to accomplish a certain task?",
            "risk": "high", "certainty": "uncertain", "color": RED
        },
        {
            "text": "Are there better tools we should be using to communicate?",
            "risk": "high", "certainty": "uncertain", "color": RED
        },
        {
            "text": "My assumption is that everyone is notified when to check off or sign off. Assumes high trust",
            "risk": "high", "certainty": "uncertain", "color": RED
        },
        {
            "text": "High uncertainty when banner rotations are not talked through month in advance. Creates high risk if we are not able to create and QA in time",
            "risk": "high", "certainty": "uncertain", "color": RED
        },
        {
            "text": "Assumption: Clear Communication & Role Ownership is muddy - High Risk, Uncertain right now",
            "risk": "high", "certainty": "uncertain", "color": RED
        },
        {
            "text": "Question: Can we add an additional level of QA at Lilly before banners go to agency?",
            "risk": "low", "certainty": "uncertain", "color": BLUE
        },
        {
            "text": "Creative teams have direct line of sight into the approval process to anticipate creative grid updates/asset delivery",
            "risk": "low", "certainty": "uncertain", "color": BLUE
        }
    ]

    # Plot items
    for item in items:
        if item["risk"] == "high" and item["certainty"] == "uncertain":
            x = grid_left + grid_width * 0.7 + random.uniform(-0.5, 0.5)
            y = grid_top + 0.3 + random.uniform(-0.2, 0.2)
        elif item["risk"] == "low" and item["certainty"] == "uncertain":
            x = grid_left + grid_width * 0.7 + random.uniform(-0.5, 0.5)
            y = grid_top + grid_height - 1 + random.uniform(-0.2, 0.2)
        elif item["risk"] == "high" and item["certainty"] == "certain":
            x = grid_left + 0.5 + random.uniform(-0.2, 0.2)
            y = grid_top + 0.3 + random.uniform(-0.2, 0.2)
        else:  # low risk, certain
            x = grid_left + 0.5 + random.uniform(-0.2, 0.2)
            y = grid_top + grid_height - 1 + random.uniform(-0.2, 0.2)

        add_sticky_note(slide, Inches(x), Inches(y), Inches(2.5), Inches(0.8), item["text"], item["color"], random.randint(-3, 3))

    # Highlight upper-right quadrant
    highlight = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(grid_left + grid_width/2), Inches(grid_top),
        Inches(grid_width/2), Inches(grid_height/2)
    )
    highlight.fill.background()
    highlight.line.color.rgb = LILLY_RED
    highlight.line.width = Pt(4)

    prs.save('/Users/V5X8512/Downloads/07_assumptions.pptx')
    print("✓ Generated: 07_assumptions.pptx")

def create_big_ideas():
    """OUTPUT 8: Big Idea Vignettes"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, KRAFT_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(8), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.text = "BIG IDEAS"
    title_frame.paragraphs[0].font.size = Pt(48)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = LILLY_RED

    # Big ideas from transcript
    ideas = [
        {
            "cluster": "ROLE CLARITY & PROCESS",
            "items": [
                {"headline": "Standardization", "description": "Standardization across lines of business and business units. HCP/Consumer function very differently based on different org structures"},
                {"headline": "Role Clarity", "description": "Role clarity among everyone involved in the process and expectations of that role"},
                {"headline": "Clear Ownership", "description": "Clear ownership of Creative Grid process within Lilly (lots of pushing to different people)"},
                {"headline": "Defined Process", "description": "Develop clear process to set expectations on what happens when within the tactic approval lifecycle"}
            ]
        },
        {
            "cluster": "COMMUNICATION & VISIBILITY",
            "items": [
                {"headline": "Visibility", "description": "ADCO/MCO: Visibility on the hand offs, so we can jump in and help/assist to keep/manage to the speed"},
                {"headline": "More Pings", "description": "More pings/teams posts. Posting to a Teams Channel and tagging marketer/CMI when handoffs are ready"},
                {"headline": "Better Notifications", "description": "Improve Notification & Handoff Clarity. Automatic notifications when a step is completed. A visible owner field for each stage"},
                {"headline": "Rotation Clarity", "description": "Clear Asset Rotation Communication. Make currently live banner rotations more clear on creative grid"}
            ]
        },
        {
            "cluster": "SYSTEMS & AUTOMATION",
            "items": [
                {"headline": "System Alignment", "description": "Better systems in place that talk to each other. Ie: notifying the right people when an asset is ready to go"},
                {"headline": "Automate Grid", "description": "Automate the Creative Grid or Build a better UI/UX. Auto-population of repeated fields, more drop-down menus, auto-notifications"},
                {"headline": "Workfront Tasks", "description": "Tasks in Adobe Workfront. Trafficking tasks implemented with POCs assigned to the tasks"},
                {"headline": "Metadata Automation", "description": "A solution that collects all needed metadata for creative campaign and compiles into creative trafficking form"}
            ]
        },
        {
            "cluster": "SPEED & QUALITY",
            "items": [
                {"headline": "Fast Track", "description": "Build a Fast Track Path for High-Urgency Messages. Pre-approved templates, pre-aligned messaging buckets, shortened review path"},
                {"headline": "QA Improvements", "description": "Revamp QA process before sent to agency (missing black borders, image not fully clickable)"},
                {"headline": "Timeline Standards", "description": "Establishing Clear, End-to-End DTC Production Timeframes. Consistency in approval process timing"},
                {"headline": "Marketer Cheat Sheet", "description": "A marketer cheat sheet. What steps MUST I check off every time to ensure fastest hand off?"}
            ]
        },
        {
            "cluster": "TRACKING & VISIBILITY",
            "items": [
                {"headline": "High Level Map", "description": "High level creative map. Need to see big picture of what we are launching when and WHY"},
                {"headline": "Status Tracker", "description": "A status tracker (Not Started → In Progress → Ready → Launched)"},
                {"headline": "Quarterly Matrix", "description": "Each marketer creates and owns a quarterly rotation matrix and aligns with the creative grid"}
            ]
        }
    ]

    y_offset = 1.2
    for cluster in ideas:
        # Cluster label
        cluster_label = slide.shapes.add_textbox(Inches(0.5), Inches(y_offset), Inches(14), Inches(0.4))
        cluster_label.text_frame.text = cluster["cluster"]
        cluster_label.text_frame.paragraphs[0].font.size = Pt(18)
        cluster_label.text_frame.paragraphs[0].font.bold = True
        cluster_label.text_frame.paragraphs[0].font.color.rgb = LILLY_BLUE

        y_offset += 0.5

        # Place vignettes
        x_offset = 0.5
        for i, idea in enumerate(cluster["items"][:4]):
            # Left note: headline + description
            add_sticky_note(
                slide,
                Inches(x_offset), Inches(y_offset),
                Inches(3.2), Inches(0.9),
                f"{idea['headline']}\n{idea['description']}",
                YELLOW, random.randint(-2, 2)
            )

            x_offset += 3.5

            if (i + 1) % 4 == 0:
                x_offset = 0.5
                y_offset += 1.1

        if x_offset != 0.5:
            y_offset += 1.2

    prs.save('/Users/V5X8512/Downloads/08_big_ideas.pptx')
    print("✓ Generated: 08_big_ideas.pptx")

def create_prioritization_grid():
    """OUTPUT 9: Prioritization Grid 2x2"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(8), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Prioritization Grid"
    title_frame.paragraphs[0].font.size = Pt(40)
    title_frame.paragraphs[0].font.bold = True

    # Draw 2x2 grid
    grid_left = 2
    grid_top = 1.5
    grid_width = 12
    grid_height = 6.5

    # Draw axes
    v_axis = slide.shapes.add_connector(2, Inches(grid_left), Inches(grid_top), Inches(grid_left), Inches(grid_top + grid_height))
    v_axis.line.width = Pt(3)
    v_axis.line.color.rgb = RGBColor(0, 0, 0)

    h_axis = slide.shapes.add_connector(1, Inches(grid_left), Inches(grid_top + grid_height/2), Inches(grid_left + grid_width), Inches(grid_top + grid_height/2))
    h_axis.line.width = Pt(3)
    h_axis.line.color.rgb = RGBColor(0, 0, 0)

    # Axis labels
    # Vertical: IMPORTANCE TO USER
    importance_high = slide.shapes.add_textbox(Inches(0.3), Inches(grid_top), Inches(1.5), Inches(0.5))
    importance_high.text_frame.text = "HIGH\nIMPORTANCE"
    importance_high.text_frame.paragraphs[0].font.size = Pt(10)
    importance_high.text_frame.paragraphs[0].font.bold = True
    importance_high.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    importance_low = slide.shapes.add_textbox(Inches(0.3), Inches(grid_top + grid_height - 0.5), Inches(1.5), Inches(0.5))
    importance_low.text_frame.text = "LOW\nIMPORTANCE"
    importance_low.text_frame.paragraphs[0].font.size = Pt(10)
    importance_low.text_frame.paragraphs[0].font.bold = True
    importance_low.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Horizontal: FEASIBILITY FOR US
    difficult = slide.shapes.add_textbox(Inches(grid_left), Inches(grid_top + grid_height + 0.2), Inches(2.5), Inches(0.4))
    difficult.text_frame.text = "DIFFICULT/EXPENSIVE"
    difficult.text_frame.paragraphs[0].font.size = Pt(10)
    difficult.text_frame.paragraphs[0].font.bold = True

    easy = slide.shapes.add_textbox(Inches(grid_left + grid_width - 2.5), Inches(grid_top + grid_height + 0.2), Inches(2.5), Inches(0.4))
    easy.text_frame.text = "EASY/CHEAP"
    easy.text_frame.paragraphs[0].font.size = Pt(10)
    easy.text_frame.paragraphs[0].font.bold = True
    easy.text_frame.paragraphs[0].alignment = PP_ALIGN.RIGHT

    # Quadrant labels
    # Upper-right: NO-BRAINERS
    no_brainers = slide.shapes.add_textbox(Inches(grid_left + grid_width * 0.65), Inches(grid_top + 0.3), Inches(3), Inches(0.5))
    no_brainers.text_frame.text = "NO-BRAINERS"
    no_brainers.text_frame.paragraphs[0].font.size = Pt(20)
    no_brainers.text_frame.paragraphs[0].font.bold = True
    no_brainers.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 100, 0)

    # Upper-left: BIG BETS
    big_bets = slide.shapes.add_textbox(Inches(grid_left + 0.3), Inches(grid_top + 0.3), Inches(3), Inches(0.5))
    big_bets.text_frame.text = "BIG BETS"
    big_bets.text_frame.paragraphs[0].font.size = Pt(20)
    big_bets.text_frame.paragraphs[0].font.bold = True
    big_bets.text_frame.paragraphs[0].font.color.rgb = LILLY_BLUE

    # Lower-right: UTILITIES
    utilities = slide.shapes.add_textbox(Inches(grid_left + grid_width * 0.65), Inches(grid_top + grid_height - 0.8), Inches(3), Inches(0.5))
    utilities.text_frame.text = "UTILITIES"
    utilities.text_frame.paragraphs[0].font.size = Pt(20)
    utilities.text_frame.paragraphs[0].font.bold = True
    utilities.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 139)

    # Lower-left: UNWISE
    unwise = slide.shapes.add_textbox(Inches(grid_left + 0.3), Inches(grid_top + grid_height - 0.8), Inches(3), Inches(0.5))
    unwise.text_frame.text = "UNWISE"
    unwise.text_frame.paragraphs[0].font.size = Pt(20)
    unwise.text_frame.paragraphs[0].font.bold = True
    unwise.text_frame.paragraphs[0].font.color.rgb = RGBColor(128, 128, 128)

    # Plot ideas
    ideas_to_plot = [
        {"idea": "⭐ Automate Grid Notifications", "quadrant": "no-brainers", "color": GREEN},
        {"idea": "⭐ Teams Channel Pings", "quadrant": "no-brainers", "color": GREEN},
        {"idea": "Role Clarity Documentation", "quadrant": "no-brainers", "color": GREEN},
        {"idea": "Marketer Cheat Sheet", "quadrant": "no-brainers", "color": GREEN},
        {"idea": "Status Tracker", "quadrant": "no-brainers", "color": GREEN},
        {"idea": "Quarterly Rotation Matrix", "quadrant": "no-brainers", "color": GREEN},
        {"idea": "⭐ Metadata Automation", "quadrant": "big-bets", "color": YELLOW},
        {"idea": "Workfront Implementation", "quadrant": "big-bets", "color": YELLOW},
        {"idea": "Complete Grid Redesign", "quadrant": "big-bets", "color": YELLOW},
        {"idea": "Standardization Across BUs", "quadrant": "big-bets", "color": YELLOW},
        {"idea": "Additional QA Layer", "quadrant": "utilities", "color": BLUE},
        {"idea": "High-Level Creative Map", "quadrant": "utilities", "color": BLUE}
    ]

    for item in ideas_to_plot:
        if item["quadrant"] == "no-brainers":
            x = grid_left + grid_width * 0.65 + random.uniform(0, 1.5)
            y = grid_top + 0.8 + random.uniform(0, 1.5)
        elif item["quadrant"] == "big-bets":
            x = grid_left + 0.3 + random.uniform(0, 1.5)
            y = grid_top + 0.8 + random.uniform(0, 1.5)
        elif item["quadrant"] == "utilities":
            x = grid_left + grid_width * 0.65 + random.uniform(0, 1.5)
            y = grid_top + grid_height - 2 + random.uniform(0, 1)
        else:  # unwise
            x = grid_left + 0.3 + random.uniform(0, 1.5)
            y = grid_top + grid_height - 2 + random.uniform(0, 1)

        add_sticky_note(slide, Inches(x), Inches(y), Inches(2.2), Inches(0.6), item["idea"], item["color"], random.randint(-3, 3))

    prs.save('/Users/V5X8512/Downloads/09_prioritization_grid.pptx')
    print("✓ Generated: 09_prioritization_grid.pptx")

def create_tobe_process_map():
    """OUTPUT 10: To-Be Process Map"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(12), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "To-Be Scenario Map: Banner Display Trafficking Process"
    title_frame.paragraphs[0].font.size = Pt(32)
    title_frame.paragraphs[0].font.bold = True

    # Process phases - future state
    phases = ["Planning & Workflow", "Creative & Production", "Review & Approval", "Trafficking & Activation", "Confirmation"]

    row_labels = ["PHASES", "DOING", "THINKING", "FEELING"]
    row_heights = [0.8, 2, 2, 2]

    y_offset = 1

    # Draw row label column
    current_y = y_offset
    for i, label in enumerate(row_labels):
        label_box = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(0.5), Inches(current_y),
            Inches(1.5), Inches(row_heights[i])
        )
        label_box.fill.solid()
        if i == 0:
            label_box.fill.fore_color.rgb = LILLY_GRAY
        else:
            label_box.fill.fore_color.rgb = RGBColor(240, 240, 240)
        label_box.line.color.rgb = RGBColor(100, 100, 100)

        label_text = label_box.text_frame
        label_text.text = label
        label_text.vertical_anchor = MSO_ANCHOR.MIDDLE
        label_text.paragraphs[0].alignment = PP_ALIGN.CENTER
        label_text.paragraphs[0].font.size = Pt(14)
        label_text.paragraphs[0].font.bold = True
        if i == 0:
            label_text.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

        current_y += row_heights[i]

    # Draw phase columns
    col_width = 2.5
    current_x = 2.2

    for phase in phases:
        phase_box = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(current_x), Inches(y_offset),
            Inches(col_width), Inches(0.8)
        )
        phase_box.fill.solid()
        phase_box.fill.fore_color.rgb = TEAL
        phase_box.line.color.rgb = RGBColor(100, 100, 100)

        phase_text = phase_box.text_frame
        phase_text.text = phase
        phase_text.vertical_anchor = MSO_ANCHOR.MIDDLE
        phase_text.paragraphs[0].alignment = PP_ALIGN.CENTER
        phase_text.paragraphs[0].font.size = Pt(11)
        phase_text.paragraphs[0].font.bold = True
        phase_text.word_wrap = True

        current_x += col_width

    # DOING row - future state
    doing_items = [
        "Quarterly matrix created\n✓ Roles defined\nBacklog aligned",
        "⭐ Auto-populated templates\nAsset build\nMetadata captured",
        "Streamlined approval\nEditor → Owner → AFD",
        "✓ Auto-notification\n⭐ Grid pre-filled\nAgency receives assets",
        "✓ Confirmation sent\nMarketer notified\nBanner live"
    ]

    current_x = 2.2
    for item in doing_items:
        add_sticky_note(slide, Inches(current_x + 0.1), Inches(y_offset + 1), Inches(col_width - 0.2), Inches(1.8), item, GREEN, random.randint(-1, 1))
        current_x += col_width

    # THINKING row - future state
    thinking_items = [
        "Clear visibility on rotation plan",
        "Templates standardized across BUs",
        "Faster approval process",
        "I know exactly who to contact",
        "Process complete, confident it's live"
    ]

    current_x = 2.2
    for item in thinking_items:
        add_sticky_note(slide, Inches(current_x + 0.1), Inches(y_offset + 3), Inches(col_width - 0.2), Inches(1.8), item, BLUE, random.randint(-1, 1))
        current_x += col_width

    # FEELING row - future state
    feeling_items = [
        "Prepared and aligned",
        "Confident and efficient",
        "Clear expectations",
        "✓ In control\n✓ Communicated well",
        "Accomplished and confident"
    ]

    current_x = 2.2
    for item in feeling_items:
        add_sticky_note(slide, Inches(current_x + 0.1), Inches(y_offset + 5), Inches(col_width - 0.2), Inches(1.8), item, YELLOW, random.randint(-1, 1))
        current_x += col_width

    # Legend
    legend_box = slide.shapes.add_textbox(Inches(0.5), Inches(8), Inches(5), Inches(0.8))
    legend_frame = legend_box.text_frame
    legend_frame.text = "✓ = Resolved Pain Point    ⭐ = New Capability/Automation"
    legend_frame.paragraphs[0].font.size = Pt(11)
    legend_frame.paragraphs[0].font.color.rgb = RGBColor(0, 100, 0)

    prs.save('/Users/V5X8512/Downloads/10_tobe_map.pptx')
    print("✓ Generated: 10_tobe_map.pptx")

if __name__ == "__main__":
    print("Generating Artifacts 7-10...")
    print("=" * 60)

    create_assumptions_grid()
    create_big_ideas()
    create_prioritization_grid()
    create_tobe_process_map()

    print("=" * 60)
    print("Completed artifacts 7-10")
