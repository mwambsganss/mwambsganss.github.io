# Design Thinking Workshop Artifact Generator Scripts

This directory contains Python scripts to generate all 17 Design Thinking Workshop artifacts from a workshop chat transcript.

## Scripts Overview

### Part 1: `generate_artifacts.py`
Generates the first 3 artifacts:
- **Output 1:** Hopes & Fears Board
- **Output 2:** Personas (6 persona cards)
- **Output 3:** Stakeholder Map

### Part 2: `generate_artifacts_part2.py`
Generates artifacts 4-6:
- **Output 4:** Empathy Maps (3 personas)
- **Output 5:** As-Is Process Map
- **Output 6:** Needs Statements

### Part 3: `generate_artifacts_part3.py`
Generates artifacts 7-10:
- **Output 7:** Assumptions and Questions 2x2 Grid
- **Output 8:** Big Idea Vignettes
- **Output 9:** Prioritization Grid
- **Output 10:** To-Be Process Map

### Part 4: `generate_artifacts_part4.py`
Generates artifacts 11-14:
- **Output 11:** Experience-Based Roadmap
- **Output 12:** Hills / Objectives
- **Output 13:** Gantt Roadmap
- **Output 14:** Resource Plan

### Part 5: `generate_artifacts_part5.py`
Generates final artifacts 15-17:
- **Output 15:** Feedback Grid
- **Output 16:** Executive Summary
- **Output 17:** Workshop Playback Deck (complete presentation)

## Requirements

```bash
pip3 install python-pptx pillow
```

## Usage

Run each script independently or all together:

```bash
# Run individual parts
python3 generate_artifacts.py
python3 generate_artifacts_part2.py
python3 generate_artifacts_part3.py
python3 generate_artifacts_part4.py
python3 generate_artifacts_part5.py

# Or create a master script to run all at once
```

## Output

All scripts generate PowerPoint (.pptx) files saved to `/Users/V5X8512/Downloads/`:
- `01_hopes_fears.pptx`
- `02_personas.pptx`
- `03_stakeholder_map.pptx`
- ... through ...
- `17_DTW_Playback_Deck.pptx`

## Design Features

All artifacts include:
- **Lilly Brand Colors** (Red: #E31837, Blue: #007AC2, Gray: #585959)
- **Sticky Note Aesthetic** with slight rotations (-3° to +3°)
- **Color-Coded Sections** (yellow, pink, orange, green, blue, teal)
- **Hand-Written Style Font** (Comic Sans MS)
- **IBM EDT-Inspired Layouts** (dark headers, kraft backgrounds)

## Customization

To apply Lilly brand templates:
1. Open generated .pptx files in PowerPoint
2. Apply branded templates
3. Replace fonts with Patrick Hand or Caveat for authentic hand-written style
4. Add texture overlays if desired
5. Export as PNG at 1920x1080 resolution

## Data Source

All content is extracted **verbatim** from workshop chat transcripts with:
- ✅ No paraphrasing or interpretation
- ✅ All participant quotes preserved exactly
- ✅ All role descriptions and pain points directly quoted
- ✅ Process steps matching transcript descriptions

## Generated: March 2, 2026
