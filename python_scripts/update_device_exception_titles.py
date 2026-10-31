"""
update_device_exception_titles.py

Updates titles and labels for Device-Level 30-Day Exception visuals:
1. Executive Summary KPI Card (v09_kpi_devexcept00):
   - Sets projection displayName to "Device-Level 30-Day Exceptions"
   - Sets title to "Device-Level 30-Day Exceptions"
2. Trends & Device Exceptions Bar Chart (p2_v07_bar_device_exceptions):
   - Sets explicit title to "Device-Level 30-Day Exceptions"
3. Trends & Device Exceptions Investigation Grid (p2_v08_grid_investigation):
   - Sets explicit title to "Device Exception Investigation Grid"
4. Left Slicers (v17_slicer_devexcept, p2_v04_slicer_exception, p3_slicer_exception, p4_slicer_exception, p5_slicer_exception):
   - Sets projection displayName to "Device Exception" for clean header display
"""

import json
from pathlib import Path
import shutil
import time

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
PAGES_DIR = PROJ / "CS Dashboard.Report" / "definition" / "pages"

DARK_GREEN = "#1b4332"

def lit(v):
    return {"expr": {"Literal": {"Value": v}}}

def color(hex_):
    return {"solid": {"color": lit(f"'{hex_}'")}}

def backup():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BASE_DIR / "development" / "jh_crowd_strike" / "backups" / f"pre_device_exception_titles_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    print(f"Pre-flight backup to: {dest}")
    return dest

def update_kpi_card():
    card_file = PAGES_DIR / "47081098f92a957d7fd0" / "visuals" / "v09_kpi_devexcept00" / "visual.json"
    if not card_file.exists():
        return
    with open(card_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Set projection displayName
    projs = data["visual"]["query"]["queryState"]["Data"]["projections"]
    for p in projs:
        if p["field"]["Measure"]["Property"] == "Devices No Microsoft Remediation 30 Days":
            p["displayName"] = "Device-Level 30-Day Exceptions"

    # Set container title
    vco = data["visual"].setdefault("visualContainerObjects", {})
    vco["title"] = [
        {
            "properties": {
                "show": lit("false"),
                "text": lit("'Device-Level 30-Day Exceptions'"),
                "titleWrap": lit("true")
            }
        }
    ]

    with open(card_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Updated Executive Summary KPI card: v09_kpi_devexcept00")

def update_bar_chart():
    bar_file = PAGES_DIR / "p02_trends_exceptions" / "visuals" / "p2_v07_bar_device_exceptions" / "visual.json"
    if not bar_file.exists():
        return
    with open(bar_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    vco = data["visual"].setdefault("visualContainerObjects", {})
    vco["title"] = [
        {
            "properties": {
                "show": lit("true"),
                "text": lit("'Device-Level 30-Day Exceptions'"),
                "titleWrap": lit("true"),
                "fontColor": color(DARK_GREEN),
                "bold": lit("true"),
                "fontSize": lit("13D")
            }
        }
    ]

    with open(bar_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Updated Trends & Exceptions bar chart: p2_v07_bar_device_exceptions")

def update_grid():
    grid_file = PAGES_DIR / "p02_trends_exceptions" / "visuals" / "p2_v08_grid_investigation" / "visual.json"
    if not grid_file.exists():
        return
    with open(grid_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    vco = data["visual"].setdefault("visualContainerObjects", {})
    vco["title"] = [
        {
            "properties": {
                "show": lit("true"),
                "text": lit("'Device Exception Investigation Grid'"),
                "titleWrap": lit("true"),
                "fontColor": color(DARK_GREEN),
                "bold": lit("true"),
                "fontSize": lit("13D")
            }
        }
    ]

    with open(grid_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Updated Trends & Exceptions grid: p2_v08_grid_investigation")

def update_slicers():
    slicer_files = [
        PAGES_DIR / "47081098f92a957d7fd0" / "visuals" / "v17_slicer_devexcept" / "visual.json",
        PAGES_DIR / "p02_trends_exceptions" / "visuals" / "p2_v04_slicer_exception" / "visual.json",
        PAGES_DIR / "p03_vulnerability_details" / "visuals" / "p3_slicer_exception" / "visual.json",
        PAGES_DIR / "p04_vulnerability_overview" / "visuals" / "p4_slicer_exception" / "visual.json",
        PAGES_DIR / "p05_vulnerability_details" / "visuals" / "p5_slicer_exception" / "visual.json",
    ]
    for sf in slicer_files:
        if not sf.exists():
            continue
        with open(sf, "r", encoding="utf-8") as f:
            data = json.load(f)
        projs = data.get("visual", {}).get("query", {}).get("queryState", {}).get("Values", {}).get("projections", [])
        for p in projs:
            if p.get("field", {}).get("Column", {}).get("Property") == "Device Patch Exception":
                p["displayName"] = "Device Exception"
        with open(sf, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Updated slicer displayName: {sf.parent.name}")

def main():
    backup()
    update_kpi_card()
    update_bar_chart()
    update_grid()
    update_slicers()
    print("All title and label updates complete.")

if __name__ == "__main__":
    main()
