#!/usr/bin/env python3
"""
Design Thinking Workshop Artifacts Generator - Part 2
Empathy Maps, Process Maps, Needs Statements
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

def create_empathy_maps():
    """OUTPUT 4: Empathy Maps"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    # Extract empathy data from transcript
    personas_empathy = [
        {
            "name": "Mia (HCP Marketer)",
            "thinks": [
                "As marketer, I have to be proactive (think 1-2 months out)",
                "I think through the HCP experience and what I want them to see more of",
                "I think about giving my CMI partners ample heads up when we have a plan"
            ],
            "feels": [
                "I feel like there are a lot of handoffs that can make me feel frustrated",
                "I feel like I let down the process when I am not fast enough entering inputs",
                "I feel a loss of control when it gets to the creative grid process"
            ],
            "says": [
                "I kick off banners, project manage it through MLR and the creative grid traffic process",
                "This can take me 5-10 minutes sometimes and even that is hard to come by",
                "There are times when banners are left hanging if I think we are set but CMI doesn't get the notification"
            ],
            "does": [
                "Kicks off banners with brand strategy",
                "Presents idea to LMS or E2E colleagues who create asset",
                "Takes through MLR to get approval",
                "Sends CMI team updated excel grid with banner rotation",
                "Fills in rotation, start, end date"
            ],
            "pains": [
                "A lot of handoffs in the process",
                "Takes 5-10 minutes to enter inputs - hard to come by",
                "Loss of control in creative grid process",
                "Communication gaps leave banners hanging"
            ],
            "gains": [
                "Wants to ensure right message gets into market",
                "Wants to feel confident process is complete",
                "Wants HCPs experiencing intended messages",
                "Wants to know when steps are incomplete to address quickly"
            ]
        },
        {
            "name": "Julie (DTC Media Lead)",
            "thinks": [
                "I'm thinking ahead",
                "I consider the full HCP experience and what placements will resonate most",
                "I try to give CMI as much advance notice as possible"
            ],
            "feels": [
                "There are constant moving pieces we are coordinating",
                "The number of handoffs can feel heavy and sometimes frustrating",
                "I feel a loss of control—communication gaps can leave banners stalled"
            ],
            "says": [
                "We need to work more strongly with the Lilly organization to understand impact when assets are not available",
                "How that dilutes our marketplace impact to drive scripts",
                "Ensures placements are strategically placed for patients/consumers to see our offerings"
            ],
            "does": [
                "Strategically determine placements for ad unit types",
                "Provide specs to TA & GCO CC&A team for ad unit creation",
                "Confirm creative grid inputs are accurate",
                "Approve it for agency hand off"
            ],
            "pains": [
                "Constant moving pieces to coordinate",
                "Items delayed/not available negatively impact plans",
                "Dilutes marketplace impact to drive scripts"
            ],
            "gains": [
                "Assets delivered on time",
                "Maintain strategic integrity of plans",
                "Impact patients",
                "Maintain marketplace investments"
            ]
        },
        {
            "name": "Molly (Media Operations)",
            "thinks": [
                "There are so many roles that constantly keep changing",
                "Its impossible to keep up with how its changing",
                "A lot of black boxes folks don't quite understand who is supposed to be doing what"
            ],
            "feels": [
                "Impossible to keep people communicating with each other on what the process is",
                "Hard to keep up with constant role changes"
            ],
            "says": [
                "Ensures trafficking handoff processes are working well",
                "Providing the necessary tools like Smartsheet",
                "Process documentation so different groups can confidently work together"
            ],
            "does": [
                "Ensures trafficking handoff processes work well",
                "Provides necessary tools like Smartsheet",
                "Creates process documentation",
                "Enables teams to work together confidently"
            ],
            "pains": [
                "Roles constantly changing",
                "Black boxes - unclear who does what",
                "When problems arise, hard to triage who to talk to"
            ],
            "gains": [
                "Understand who is doing what",
                "When problems arise, can triage who to talk to",
                "Dig into what went wrong"
            ]
        }
    ]

    for persona_data in personas_empathy:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        add_background(slide, prs, KRAFT_BG)

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(10), Inches(0.5))
        title_frame = title_box.text_frame
        title_frame.text = f"Empathy Map: {persona_data['name']}"
        title_frame.paragraphs[0].font.size = Pt(36)
        title_frame.paragraphs[0].font.bold = True

        # Avatar in center
        avatar = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(7), Inches(3.8), Inches(2), Inches(2))
        avatar.fill.solid()
        avatar.fill.fore_color.rgb = RGBColor(200, 200, 200)
        avatar.line.color.rgb = RGBColor(100, 100, 100)
        avatar.line.width = Pt(2)

        avatar_text = avatar.text_frame
        avatar_text.text = persona_data['name'].split('(')[0].strip()
        avatar_text.paragraphs[0].alignment = PP_ALIGN.CENTER
        avatar_text.vertical_anchor = MSO_ANCHOR.MIDDLE
        avatar_text.paragraphs[0].font.size = Pt(16)
        avatar_text.paragraphs[0].font.bold = True

        # Quadrant labels
        quadrants = [
            ("THINKS", 0.5, 1, 6.5, 3.5),
            ("FEELS", 9.5, 1, 6, 3.5),
            ("SAYS", 0.5, 6, 6.5, 2.5),
            ("DOES", 9.5, 6, 6, 2.5)
        ]

        for label, x, y, w, h in quadrants:
            label_box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(2), Inches(0.4))
            label_frame = label_box.text_frame
            label_frame.text = label
            label_frame.paragraphs[0].font.size = Pt(20)
            label_frame.paragraphs[0].font.bold = True
            label_frame.paragraphs[0].font.color.rgb = RGBColor(0, 0, 0)

        # Add sticky notes for THINKS (top-left)
        for i, item in enumerate(persona_data['thinks'][:3]):
            add_sticky_note(slide, Inches(0.5 + i*2.1), Inches(1.5), Inches(2), Inches(0.8), item, BLUE, random.randint(-2, 2))

        # Add sticky notes for FEELS (top-right)
        for i, item in enumerate(persona_data['feels'][:3]):
            add_sticky_note(slide, Inches(9.5 + i*2.1), Inches(1.5), Inches(2), Inches(0.8), item, PINK, random.randint(-2, 2))

        # Add sticky notes for SAYS (bottom-left)
        for i, item in enumerate(persona_data['says'][:3]):
            add_sticky_note(slide, Inches(0.5 + i*2.1), Inches(6.5), Inches(2), Inches(0.8), item, YELLOW, random.randint(-2, 2))

        # Add sticky notes for DOES (bottom-right)
        for i, item in enumerate(persona_data['does'][:3]):
            add_sticky_note(slide, Inches(9.5 + i*2.1), Inches(6.5), Inches(2), Inches(0.8), item, GREEN, random.randint(-2, 2))

        # Bottom strips
        # PAINS (left)
        pains_label = slide.shapes.add_textbox(Inches(0.5), Inches(8), Inches(2), Inches(0.3))
        pains_label.text_frame.text = "PAINS"
        pains_label.text_frame.paragraphs[0].font.size = Pt(16)
        pains_label.text_frame.paragraphs[0].font.bold = True
        pains_label.text_frame.paragraphs[0].font.color.rgb = RGBColor(139, 0, 0)

        for i, pain in enumerate(persona_data['pains'][:3]):
            add_sticky_note(slide, Inches(0.5 + i*2.1), Inches(8.3), Inches(2), Inches(0.6), pain, PINK, random.randint(-2, 2))

        # GAINS (right)
        gains_label = slide.shapes.add_textbox(Inches(9.5), Inches(8), Inches(2), Inches(0.3))
        gains_label.text_frame.text = "GAINS"
        gains_label.text_frame.paragraphs[0].font.size = Pt(16)
        gains_label.text_frame.paragraphs[0].font.bold = True
        gains_label.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 100, 0)

        for i, gain in enumerate(persona_data['gains'][:3]):
            add_sticky_note(slide, Inches(9.5 + i*2.1), Inches(8.3), Inches(2), Inches(0.6), gain, GREEN, random.randint(-2, 2))

    prs.save('/Users/V5X8512/Downloads/04_empathy_maps.pptx')
    print("✓ Generated: 04_empathy_maps.pptx")

def create_asis_process_map():
    """OUTPUT 5: As-Is Process Map"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.2), Inches(12), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "As-Is Scenario Map: Banner Display Trafficking Process"
    title_frame.paragraphs[0].font.size = Pt(32)
    title_frame.paragraphs[0].font.bold = True

    # Process phases from transcript
    phases = ["Planning & Workflow", "Creative & Production", "Review & Approval", "Trafficking & Activation", "Tactic Destruction"]

    # Row labels
    row_labels = ["PHASES", "DOING", "THINKING", "FEELING"]
    row_heights = [0.8, 2, 2, 2]
    row_colors = [LILLY_GRAY, YELLOW, BLUE, PINK]

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

    # Phase headers
    for phase in phases:
        phase_box = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE,
            Inches(current_x), Inches(y_offset),
            Inches(col_width), Inches(0.8)
        )
        phase_box.fill.solid()
        phase_box.fill.fore_color.rgb = ORANGE
        phase_box.line.color.rgb = RGBColor(100, 100, 100)

        phase_text = phase_box.text_frame
        phase_text.text = phase
        phase_text.vertical_anchor = MSO_ANCHOR.MIDDLE
        phase_text.paragraphs[0].alignment = PP_ALIGN.CENTER
        phase_text.paragraphs[0].font.size = Pt(11)
        phase_text.paragraphs[0].font.bold = True
        phase_text.word_wrap = True

        current_x += col_width

    # DOING row content
    doing_items = [
        "Quarterly alignment\nBacklog refinement\nSprint planning",
        "Asset build per templates\nReadiness checks",
        "Editor → MLRO → Project Owner → AFD",
        "Assets + grid details sent to agencies\nQA assets\nBuild tags",
        "Upon expiration"
    ]

    current_x = 2.2
    for item in doing_items:
        add_sticky_note(slide, Inches(current_x + 0.1), Inches(y_offset + 1), Inches(col_width - 0.2), Inches(1.8), item, YELLOW, random.randint(-1, 1))
        current_x += col_width

    # THINKING row content
    thinking_items = [
        "Need to align with brand strategy",
        "Must follow templates and specs",
        "Multiple approval layers needed",
        "Who has the files? Are they correct?",
        "Is banner out of market?"
    ]

    current_x = 2.2
    for item in thinking_items:
        add_sticky_note(slide, Inches(current_x + 0.1), Inches(y_offset + 3), Inches(col_width - 0.2), Inches(1.8), item, BLUE, random.randint(-1, 1))
        current_x += col_width

    # FEELING row content
    feeling_items = [
        "Proactive planning needed",
        "Rushing to meet deadlines",
        "Waiting for approvals",
        "⚡ Frustrated by handoffs\n⚡ Loss of control\n⚡ Communication gaps",
        "Relief when complete"
    ]

    current_x = 2.2
    for i, item in enumerate(feeling_items):
        color = PINK if i == 3 else PINK  # Highlight pain point
        add_sticky_note(slide, Inches(current_x + 0.1), Inches(y_offset + 5), Inches(col_width - 0.2), Inches(1.8), item, color, random.randint(-1, 1))
        current_x += col_width

    # Add pain point flags
    pain_box = slide.shapes.add_textbox(Inches(10), Inches(5.2), Inches(2.5), Inches(0.4))
    pain_box.text_frame.text = "⚡ = PAIN POINT"
    pain_box.text_frame.paragraphs[0].font.size = Pt(12)
    pain_box.text_frame.paragraphs[0].font.color.rgb = RGBColor(139, 0, 0)

    prs.save('/Users/V5X8512/Downloads/05_asis_map.pptx')
    print("✓ Generated: 05_asis_map.pptx")

def create_needs_statements():
    """OUTPUT 6: Needs Statements"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, KRAFT_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.6))
    title_frame = title_box.text_frame
    title_frame.text = "[User] needs a way to... so that..."
    title_frame.paragraphs[0].font.size = Pt(40)
    title_frame.paragraphs[0].font.bold = True

    # Needs statements extracted from transcript
    needs = [
        {
            "persona": "Mia (HCP Marketer)",
            "need": "easily see rotation",
            "benefit": "I can quickly assess HCP experience and understand if changes are needed"
        },
        {
            "persona": "Mia (HCP Marketer)",
            "need": "ensure when banners went to customers",
            "benefit": "I feel confident that the process is complete and our HCPs are experiencing the intended messages"
        },
        {
            "persona": "Mia (HCP Marketer)",
            "need": "know when steps are incomplete",
            "benefit": "myself or team can address for speedy launches"
        },
        {
            "persona": "Julie (DTC Media)",
            "need": "ensure assets are delivered on time",
            "benefit": "to maintain strategic integrity of plans to impact patients, maintain marketplace investments, and protect agency resources"
        },
        {
            "persona": "Molly (Media Operations)",
            "need": "understand who is doing what",
            "benefit": "when problems arise, we can triage who to talk to and dig into what went wrong"
        },
        {
            "persona": "Matt (Digital Brand Lead)",
            "need": "a solution to know when assets are to be trafficked along with all information needed",
            "benefit": "to ensure the accuracy of the hand-off"
        },
        {
            "persona": "Matt (Digital Brand Lead)",
            "need": "a process or confirmation on when the banner is out of market",
            "benefit": "to ensure we are compliant with our tactic expiration"
        },
        {
            "persona": "HCP Agency Team",
            "need": "clear communication, role ownership and rotation direction from the creative grid",
            "benefit": "to avoid delays and mitigate the risk for errors"
        },
        {
            "persona": "HCP Agency Team",
            "need": "banner assets to come over without errors",
            "benefit": "to avoid delays in getting assets into market"
        },
        {
            "persona": "Consumer Agency",
            "need": "accurate creative grid updates and asset delivery",
            "benefit": "to adhere to SLA, and especially allow priority campaigns to break timeline when approvals are delayed"
        },
        {
            "persona": "ADCO",
            "need": "to know who to connect to when files or handoffs are not complete",
            "benefit": "we can ensure speed of the work"
        },
        {
            "persona": "ADCO",
            "need": "confirmation from media partner once files are received and when QA has started",
            "benefit": "we can track progress and manage timeline expectations"
        }
    ]

    # Cluster theme
    theme_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.2), Inches(15), Inches(0.5))
    theme_frame = theme_box.text_frame
    theme_frame.text = "COMMUNICATION & VISIBILITY"
    theme_frame.paragraphs[0].font.size = Pt(24)
    theme_frame.paragraphs[0].font.bold = True
    theme_frame.paragraphs[0].font.color.rgb = LILLY_RED
    theme_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Place needs statements
    y_offset = 2
    x_offset = 0.5
    col_count = 0

    for need in needs[:12]:
        statement = f"{need['persona']} needs a way to {need['need']} so that {need['benefit']}"

        add_sticky_note(
            slide,
            Inches(x_offset), Inches(y_offset),
            Inches(4.5), Inches(1.2),
            statement, YELLOW, random.randint(-2, 2)
        )

        col_count += 1
        if col_count == 3:
            col_count = 0
            x_offset = 0.5
            y_offset += 1.5
        else:
            x_offset += 5

    prs.save('/Users/V5X8512/Downloads/06_needs_statements.pptx')
    print("✓ Generated: 06_needs_statements.pptx")

if __name__ == "__main__":
    print("Generating Artifacts 4-6...")
    print("=" * 60)

    create_empathy_maps()
    create_asis_process_map()
    create_needs_statements()

    print("=" * 60)
    print("Completed artifacts 4-6")
