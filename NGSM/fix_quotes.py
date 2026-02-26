#!/usr/bin/env python3
"""Fix quote issues in analyze_cortex_capabilities.py"""

with open('analyze_cortex_capabilities.py', 'r') as f:
    lines = f.readlines()

fixed_lines = []
for line in lines:
    # Fix lines with mixed quotes in agent_analysis dictionary
    if '": "✅ **' in line and "': " in line:
        # Replace the last occurrence of ': with ":
        parts = line.rsplit("': ", 1)
        if len(parts) == 2:
            line = parts[0] + '": ' + parts[1]

    fixed_lines.append(line)

with open('analyze_cortex_capabilities.py', 'w') as f:
    f.writelines(fixed_lines)

print("Fixed all quote mismatches")
