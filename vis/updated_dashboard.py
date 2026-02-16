#!/usr/bin/env python3
"""
Refresh the NER comparison dashboard with latest data from output/output.json.
Usage: python generate_dashboard.py [input_file]
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DEFAULT_INPUT = SCRIPT_DIR.parent / "output" / "output.json"
DASHBOARD_HTML = SCRIPT_DIR / "dashboard.html"


def refresh_dashboard(input_file=None):
    input_path = Path(input_file) if input_file else DEFAULT_INPUT
    if not input_path.exists():
        print(f"Error: Input file '{input_path}' not found")
        sys.exit(1)

    if not DASHBOARD_HTML.exists():
        print(f"Error: Dashboard template '{DASHBOARD_HTML}' not found")
        sys.exit(1)

    # Read and validate JSONL data
    with open(input_path, "r", encoding="utf-8") as f:
        raw_data = f.read().strip()

    records = []
    for i, line in enumerate(raw_data.split("\n"), 1):
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON on line {i}: {e}")

    # Escape for JS template literal
    safe_data = raw_data.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    # Read the dashboard HTML
    with open(DASHBOARD_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # Replace the data inside the RAW_JSON template literal
    pattern = r"(const RAW_JSON = `).*?(`;\s*\nlet DATA;)"
    replacement = rf"\g<1>{safe_data}\g<2>"
    new_html, count = re.subn(pattern, replacement, html, count=1, flags=re.DOTALL)

    if count == 0:
        print("Error: Could not find RAW_JSON placeholder in dashboard.html")
        sys.exit(1)

    with open(DASHBOARD_HTML, "w", encoding="utf-8") as f:
        f.write(new_html)

    algorithms = sorted(set(r.get("Algorithm", "?") for r in records))
    test_cases = sorted(set(r.get("Test_Case", "?") for r in records))
    print(f"Dashboard refreshed with {len(records)} records")
    print(f"  Algorithms: {', '.join(algorithms)}")
    print(f"  Test cases: {', '.join(test_cases)}")
    print(f"  Output: {DASHBOARD_HTML}")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else None
    refresh_dashboard(input_file)
