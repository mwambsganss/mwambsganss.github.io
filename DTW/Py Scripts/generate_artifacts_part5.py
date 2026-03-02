#!/usr/bin/env python3
"""
Design Thinking Workshop Artifacts Generator - Part 5
Feedback Grid, Executive Summary, Workshop Playback Deck
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
        paragraph.font.size = Pt(9)
        paragraph.font.name = "Comic Sans MS"
        paragraph.font.color.rgb = RGBColor(0, 0, 0)
    return note

def create_feedback_grid():
    """OUTPUT 15: Feedback Grid"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, KRAFT_BG)

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(8), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Feedback Grid"
    title_frame.paragraphs[0].font.size = Pt(40)
    title_frame.paragraphs[0].font.bold = True

    # Draw 2x2 grid
    grid_left = 1
    grid_top = 1.2
    grid_width = 14
    grid_height = 7

    # Vertical divider
    v_line = slide.shapes.add_connector(2, Inches(grid_left + grid_width/2), Inches(grid_top), Inches(grid_left + grid_width/2), Inches(grid_top + grid_height))
    v_line.line.width = Pt(4)
    v_line.line.color.rgb = RGBColor(0, 0, 0)

    # Horizontal divider
    h_line = slide.shapes.add_connector(1, Inches(grid_left), Inches(grid_top + grid_height/2), Inches(grid_left + grid_width), Inches(grid_top + grid_height/2))
    h_line.line.width = Pt(4)
    h_line.line.color.rgb = RGBColor(0, 0, 0)

    # Quadrant labels
    quadrant_labels = [
        ("THINGS THAT WORKED +", grid_left + 0.3, grid_top + 0.2, GREEN),
        ("THINGS TO CHANGE △", grid_left + grid_width/2 + 0.3, grid_top + 0.2, PINK),
        ("QUESTIONS WE STILL HAVE ?", grid_left + 0.3, grid_top + grid_height/2 + 0.2, YELLOW),
        ("NEW IDEAS TO TRY 💡", grid_left + grid_width/2 + 0.3, grid_top + grid_height/2 + 0.2, BLUE)
    ]

    for label, x, y, color in quadrant_labels:
        label_box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(6), Inches(0.4))
        label_frame = label_box.text_frame
        label_frame.text = label
        label_frame.paragraphs[0].font.size = Pt(18)
        label_frame.paragraphs[0].font.bold = True

    # Things That Worked (upper-left)
    worked_items = [
        "Workshop format brought all stakeholders together",
        "Transcript capture of all perspectives",
        "Role-by-role empathy mapping",
        "Clear identification of pain points"
    ]

    y = grid_top + 0.8
    for item in worked_items:
        add_sticky_note(slide, Inches(grid_left + 0.3 + random.uniform(0, 2)), Inches(y), Inches(3), Inches(0.6), item, GREEN, random.randint(-2, 2))
        y += 0.8

    # Things To Change (upper-right)
    change_items = [
        "Need more time for roadmap prioritization discussion",
        "Should include more digital production team members",
        "Follow-up session needed to finalize ownership",
        "Need executive sponsors identified upfront"
    ]

    y = grid_top + 0.8
    for item in change_items:
        add_sticky_note(slide, Inches(grid_left + grid_width/2 + 0.3 + random.uniform(0, 2)), Inches(y), Inches(3), Inches(0.6), item, PINK, random.randint(-2, 2))
        y += 0.8

    # Questions We Still Have (lower-left)
    questions = [
        "What is timeline for implementing automated notifications?",
        "Who will own the RACI documentation?",
        "What budget is available for Workfront integration?",
        "How do we align HCP and Consumer processes?",
        "What metrics will we track for success?"
    ]

    y = grid_top + grid_height/2 + 0.8
    x_offset = 0
    for i, item in enumerate(questions):
        if i == 3:
            y += 0.8
            x_offset = 0
        add_sticky_note(slide, Inches(grid_left + 0.3 + x_offset), Inches(y), Inches(3), Inches(0.6), item, YELLOW, random.randint(-2, 2))
        x_offset += 3.3

    # New Ideas (lower-right)
    new_ideas = [
        "⭐ Consider AI/ML for predicting banner performance",
        "Create banner production SLA dashboard",
        "⭐ Explore natural language grid input",
        "Monthly cross-team sync meetings",
        "⭐ Chatbot for 'who owns what' questions"
    ]

    y = grid_top + grid_height/2 + 0.8
    x_offset = 0
    for i, item in enumerate(new_ideas):
        if i == 3:
            y += 0.8
            x_offset = 0
        add_sticky_note(slide, Inches(grid_left + grid_width/2 + 0.3 + x_offset), Inches(y), Inches(3), Inches(0.6), item, BLUE, random.randint(-2, 2))
        x_offset += 3.3

    prs.save('/Users/V5X8512/Downloads/15_feedback_grid.pptx')
    print("✓ Generated: 15_feedback_grid.pptx")

def create_executive_summary():
    """OUTPUT 16: Executive Summary"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Dark header bar
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.2))
    header.fill.solid()
    header.fill.fore_color.rgb = LILLY_RED
    header.line.fill.background()

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.7))
    title_frame = title_box.text_frame
    title_frame.text = "Banner Trafficking Workshop - Executive Summary"
    title_frame.paragraphs[0].font.size = Pt(36)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

    # Background
    add_background(slide, prs, WHITE_BG)
    slide.shapes._spTree.remove(header._element)
    slide.shapes._spTree.insert(len(slide.shapes._spTree), header._element)

    # Workshop Details
    details_box = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(7), Inches(0.8))
    details_frame = details_box.text_frame
    details_frame.text = "WORKSHOP: Banner Display Trafficking & Handoff Process Design Thinking Session\nDATE: January 29, 2026\nPARTICIPANTS: ADCO, MCO, Marketers (HCP/DTC), Media Leads, Media Ops, Digital Brand Lead, Campaign Execution, Agencies (CMI, PA)"
    details_frame.paragraphs[0].font.size = Pt(10)
    details_frame.paragraphs[0].font.bold = True

    # Problem Statement
    section_y = 2.5
    section_label = slide.shapes.add_textbox(Inches(0.5), Inches(section_y), Inches(6), Inches(0.3))
    section_label.text_frame.text = "🎯 PROBLEM STATEMENT"
    section_label.text_frame.paragraphs[0].font.size = Pt(14)
    section_label.text_frame.paragraphs[0].font.bold = True
    section_label.text_frame.paragraphs[0].font.color.rgb = LILLY_RED

    add_sticky_note(slide, Inches(0.5), Inches(section_y + 0.35), Inches(7), Inches(0.8),
                    "Outline the banner request, production, trafficking and handoff process with focus on trafficking and handoff. Identify key roles, pain points, communication gaps, and potential areas of automation across business lines.",
                    YELLOW, -1)

    # Key User
    section_y = 3.8
    section_label = slide.shapes.add_textbox(Inches(0.5), Inches(section_y), Inches(6), Inches(0.3))
    section_label.text_frame.text = "👤 KEY USERS"
    section_label.text_frame.paragraphs[0].font.size = Pt(14)
    section_label.text_frame.paragraphs[0].font.bold = True
    section_label.text_frame.paragraphs[0].font.color.rgb = LILLY_BLUE

    users_text = "Marketers (HCP & DTC), Media Leads, Agency Teams (CMI, PA), ADCO/MCO, Digital Brand Leads, Campaign Execution, Media Operations"
    add_sticky_note(slide, Inches(0.5), Inches(section_y + 0.35), Inches(7), Inches(0.6), users_text, BLUE, 1)

    # Top 3 Insights (right column)
    section_y = 2.5
    section_label = slide.shapes.add_textbox(Inches(8.5), Inches(section_y), Inches(6), Inches(0.3))
    section_label.text_frame.text = "💡 TOP 3 INSIGHTS"
    section_label.text_frame.paragraphs[0].font.size = Pt(14)
    section_label.text_frame.paragraphs[0].font.bold = True
    section_label.text_frame.paragraphs[0].font.color.rgb = LILLY_BLUE

    insights = [
        "Roles constantly changing - impossible to keep up with who does what",
        "Too many handoffs create loss of control and communication gaps",
        "No clear standard on grid ownership, trafficking, and fixing failures"
    ]
    y = section_y + 0.35
    for insight in insights:
        add_sticky_note(slide, Inches(8.5), Inches(y), Inches(7), Inches(0.5), insight, PINK, random.randint(-2, 2))
        y += 0.6

    # Top Pain Points
    section_y = 5
    section_label = slide.shapes.add_textbox(Inches(0.5), Inches(section_y), Inches(6), Inches(0.3))
    section_label.text_frame.text = "⚡ TOP 3 PAIN POINTS"
    section_label.text_frame.paragraphs[0].font.size = Pt(14)
    section_label.text_frame.paragraphs[0].font.bold = True
    section_label.text_frame.paragraphs[0].font.color.rgb = RGBColor(139, 0, 0)

    pains = [
        "Communication gaps leave banners hanging - unclear who moves it forward",
        "Black boxes - unclear who owns what step in the process",
        "5-15 day QA process delays with frequent revisions and swirl"
    ]
    y = section_y + 0.35
    for pain in pains:
        add_sticky_note(slide, Inches(0.5), Inches(y), Inches(7), Inches(0.5), pain, ORANGE, random.randint(-2, 2))
        y += 0.6

    # Top 5 Big Ideas
    section_y = 5
    section_label = slide.shapes.add_textbox(Inches(8.5), Inches(section_y), Inches(6), Inches(0.3))
    section_label.text_frame.text = "🚀 TOP 5 BIG IDEAS"
    section_label.text_frame.paragraphs[0].font.size = Pt(14)
    section_label.text_frame.paragraphs[0].font.bold = True
    section_label.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 100, 0)

    big_ideas = [
        "⭐ Automated grid notifications when steps complete",
        "Clear role clarity documentation (RACI)",
        "⭐ Metadata auto-population from source systems",
        "Teams channel pings tagging next person",
        "Fast-track path for high-urgency messages"
    ]
    y = section_y + 0.35
    for idea in big_ideas:
        add_sticky_note(slide, Inches(8.5), Inches(y), Inches(7), Inches(0.45), idea, GREEN, random.randint(-2, 2))
        y += 0.55

    # Hills
    section_y = 6.8
    section_label = slide.shapes.add_textbox(Inches(0.5), Inches(section_y), Inches(14), Inches(0.3))
    section_label.text_frame.text = "⛰️ AGREED HILLS"
    section_label.text_frame.paragraphs[0].font.size = Pt(14)
    section_label.text_frame.paragraphs[0].font.bold = True
    section_label.text_frame.paragraphs[0].font.color.rgb = LILLY_RED

    hill_text = "Marketers and Media Teams complete banner trafficking from AFD to live in 1 day with zero communication gaps, reducing time to market by 80%"
    add_sticky_note(slide, Inches(0.5), Inches(section_y + 0.35), Inches(15), Inches(0.5), hill_text, TEAL, 0)

    # Next Steps
    section_y = 7.5
    section_label = slide.shapes.add_textbox(Inches(0.5), Inches(section_y), Inches(14), Inches(0.3))
    section_label.text_frame.text = "✅ IMMEDIATE NEXT STEPS"
    section_label.text_frame.paragraphs[0].font.size = Pt(14)
    section_label.text_frame.paragraphs[0].font.bold = True
    section_label.text_frame.paragraphs[0].font.color.rgb = LILLY_BLUE

    next_steps = [
        "1. Matt & Greg synthesize workshop data and present summary back to group",
        "2. Schedule 1-hour follow-up to align on priorities and assign ownership",
        "3. Launch RACI documentation effort (Owner: Media Ops - Molly)",
        "4. Pilot Teams channel notifications for banner handoffs (Quick Win)"
    ]
    next_steps_box = slide.shapes.add_textbox(Inches(0.5), Inches(section_y + 0.35), Inches(15), Inches(1))
    next_steps_frame = next_steps_box.text_frame
    for step in next_steps:
        p = next_steps_frame.add_paragraph() if next_steps_frame.text else next_steps_frame.paragraphs[0]
        p.text = step
        p.font.size = Pt(10)
        p.space_after = Pt(3)

    prs.save('/Users/V5X8512/Downloads/16_executive_summary.pptx')
    print("✓ Generated: 16_executive_summary.pptx")

def create_playback_deck():
    """OUTPUT 17: Workshop Recap Playback Deck"""
    prs = Presentation()
    prs.slide_width = Inches(16)
    prs.slide_height = Inches(9)

    # Slide 1: Cover
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(9))
    header.fill.solid()
    header.fill.fore_color.rgb = LILLY_RED
    header.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(2), Inches(3), Inches(12), Inches(1.5))
    title_frame = title_box.text_frame
    title_frame.text = "Banner Display Trafficking\nDesign Thinking Workshop\nPlayback"
    title_frame.paragraphs[0].font.size = Pt(54)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    title_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    subtitle_box = slide.shapes.add_textbox(Inches(2), Inches(5), Inches(12), Inches(1))
    subtitle_frame = subtitle_box.text_frame
    subtitle_frame.text = "January 29, 2026\nLilly Marketing Operations, Digital, Media, and Agency Teams"
    subtitle_frame.paragraphs[0].font.size = Pt(18)
    subtitle_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    subtitle_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    # Slide 2: Agenda and Objectives
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1))
    header.fill.solid()
    header.fill.fore_color.rgb = LILLY_GRAY
    header.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(10), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Workshop Objectives"
    title_frame.paragraphs[0].font.size = Pt(32)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

    content_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(14), Inches(6))
    content_frame = content_box.text_frame
    objectives = [
        "Outline step-by-step the process of display banner request, production, trafficking and handoff",
        "Identify key roles and systems used",
        "Identify pain points and key communications gaps within the process",
        "Identify potential areas of automation or standardization across business lines (HCP & Commercial)",
        "Determine clear next steps to address pain points and possible solutions"
    ]
    for obj in objectives:
        p = content_frame.add_paragraph() if content_frame.text else content_frame.paragraphs[0]
        p.text = f"• {obj}"
        p.font.size = Pt(16)
        p.space_after = Pt(12)

    participants_box = slide.shapes.add_textbox(Inches(1), Inches(5.5), Inches(14), Inches(2.5))
    participants_frame = participants_box.text_frame
    participants_frame.text = "PARTICIPANTS: ADCO (Carrie Sieglitz), MCO (Jordyn King), DBL (Matt Casolaro), Digital PM (Ravi, Krutika), Creative (Ruchi), Marketers (Jamie Doyle, Mia McCrumb, Brandon), Media Leads (Julie Gogan, Alex Lund), Media Ops (Molly Hudlow, Angela), Agencies (CMI - Jenn Margiloff, PA - Alex Fox)"
    participants_frame.paragraphs[0].font.size = Pt(12)
    participants_frame.paragraphs[0].font.italic = True

    # Slide 3: Personas Summary
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, KRAFT_BG)

    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1))
    header.fill.solid()
    header.fill.fore_color.rgb = LILLY_GRAY
    header.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(10), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Key Personas"
    title_frame.paragraphs[0].font.size = Pt(32)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

    personas_summary = [
        ("HCP Marketer (Mia)", "I feel like there are a lot of handoffs that can make me feel frustrated"),
        ("DTC Media Lead (Julie)", "We need to understand impact when assets are not available"),
        ("HCP Agency (Jenn)", "CMI often has to help facilitate to see it through to completion"),
        ("Media Operations (Molly)", "Roles constantly changing - impossible to keep up")
    ]

    x, y = 1, 1.5
    for name, quote in personas_summary:
        add_sticky_note(slide, Inches(x), Inches(y), Inches(6.5), Inches(0.8), f"{name}\n\"{quote}\"", YELLOW, random.randint(-2, 2))
        x += 7.5
        if x > 10:
            x = 1
            y += 1.2

    # Slide 4: Key Insights
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1))
    header.fill.solid()
    header.fill.fore_color.rgb = LILLY_RED
    header.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(10), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Key Insights from Empathy Work"
    title_frame.paragraphs[0].font.size = Pt(32)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

    insights_list = [
        "Roles constantly changing across organization - impossible to keep people communicating",
        "Black boxes everywhere - unclear who is supposed to be doing what",
        "Communication gaps leave banners hanging - assumptions that other team is moving forward",
        "Marketers feel loss of control once banner enters creative grid process",
        "5-15 day QA process creates delays and missed marketplace windows",
        "No clear standard on who fills grids, who traffics, who fixes failures",
        "Too many cooks in the kitchen for trafficking - roles not clearly owned"
    ]

    x, y = 0.5, 1.5
    for i, insight in enumerate(insights_list):
        add_sticky_note(slide, Inches(x), Inches(y), Inches(4.5), Inches(0.8), insight, PINK, random.randint(-2, 2))
        x += 5
        if (i + 1) % 3 == 0:
            x = 0.5
            y += 1.2

    # Slide 5: Hills
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1))
    header.fill.solid()
    header.fill.fore_color.rgb = LILLY_RED
    header.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(10), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Our Hills (Success Outcomes)"
    title_frame.paragraphs[0].font.size = Pt(32)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

    hills_text = """▲ WHO: Marketers and Media Teams
WHAT: Complete banner trafficking from AFD to live in market within 1 day with zero communication gaps
WOW: Reducing time to market by 80% and eliminating all handoff-related delays

▲ WHO: All trafficking process stakeholders
WHAT: Know exactly who owns each step, receive automated notifications when it's their turn
WOW: Achieving 100% role clarity and eliminating all black box confusion

▲ WHO: HCP and Consumer Agencies
WHAT: Receive complete, accurate, error-free assets with all metadata in single automated handoff
WOW: Reducing agency QA rework by 90% and meeting SLA requirements consistently"""

    content_box = slide.shapes.add_textbox(Inches(1), Inches(1.5), Inches(14), Inches(6))
    content_frame = content_box.text_frame
    content_frame.text = hills_text
    content_frame.paragraphs[0].font.size = Pt(14)
    content_frame.paragraphs[0].font.name = "Courier New"

    # Slide 6: Next Steps
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_background(slide, prs, WHITE_BG)

    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1))
    header.fill.solid()
    header.fill.fore_color.rgb = LILLY_BLUE
    header.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(10), Inches(0.5))
    title_frame = title_box.text_frame
    title_frame.text = "Next Steps & Owners"
    title_frame.paragraphs[0].font.size = Pt(32)
    title_frame.paragraphs[0].font.bold = True
    title_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)

    next_steps_data = [
        ("Matt & Greg synthesize workshop data", "Matt/Greg", "Week of Feb 5"),
        ("Schedule 1-hour follow-up alignment session", "Molly", "Week of Feb 12"),
        ("Launch RACI documentation", "Media Ops - Molly", "Month 1"),
        ("Pilot Teams channel notifications", "Media Ops", "Month 1"),
        ("Create marketer cheat sheet", "ADCO - Carrie", "Month 1"),
        ("Status tracker implementation", "TBD", "Month 2-3")
    ]

    # Table
    headers = ["Action", "Owner", "Target"]
    col_widths = [6, 3, 2]
    x = 1
    y = 1.5

    for i, header in enumerate(headers):
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(col_widths[i]), Inches(0.4))
        box.fill.solid()
        box.fill.fore_color.rgb = LILLY_GRAY
        box.line.color.rgb = RGBColor(100, 100, 100)
        box.text_frame.text = header
        box.text_frame.paragraphs[0].font.size = Pt(12)
        box.text_frame.paragraphs[0].font.bold = True
        box.text_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
        box.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        x += col_widths[i]

    y += 0.4
    for action, owner, target in next_steps_data:
        x = 1
        for i, text in enumerate([action, owner, target]):
            box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(col_widths[i]), Inches(0.35))
            box.fill.solid()
            box.fill.fore_color.rgb = WHITE_BG
            box.line.color.rgb = RGBColor(180, 180, 180)
            box.text_frame.text = text
            box.text_frame.paragraphs[0].font.size = Pt(10)
            box.text_frame.margin_left = Inches(0.05)
            box.text_frame.word_wrap = True
            x += col_widths[i]
        y += 0.35

    # Final slide: Thank you
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(9))
    header.fill.solid()
    header.fill.fore_color.rgb = LILLY_RED
    header.line.fill.background()

    thank_you_box = slide.shapes.add_textbox(Inches(2), Inches(3.5), Inches(12), Inches(2))
    thank_you_frame = thank_you_box.text_frame
    thank_you_frame.text = "Thank You"
    thank_you_frame.paragraphs[0].font.size = Pt(72)
    thank_you_frame.paragraphs[0].font.bold = True
    thank_you_frame.paragraphs[0].font.color.rgb = RGBColor(255, 255, 255)
    thank_you_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

    prs.save('/Users/V5X8512/Downloads/17_DTW_Playback_Deck.pptx')
    print("✓ Generated: 17_DTW_Playback_Deck.pptx")

if __name__ == "__main__":
    print("Generating Final Artifacts 15-17...")
    print("=" * 60)

    create_feedback_grid()
    create_executive_summary()
    create_playback_deck()

    print("=" * 60)
    print("✅ ALL 17 ARTIFACTS COMPLETED!")
