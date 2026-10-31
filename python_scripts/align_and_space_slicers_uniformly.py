#!/usr/bin/env python3
"""
align_and_space_slicers_uniformly.py

Aligns and uniformly spaces all 6 slicers on the left filter shelf
across all active dashboard pages:
- Executive Summary (47081098f92a957d7fd0)
- Remediation Compliance (p03_vulnerability_details)
- Vulnerability Details (p05_vulnerability_details)

Uniform Geometry:
- Horizontal: x = 28 px, width = 275 px (centered in left filter shelf)
- Height: 72 px
- Uniform pitch: 82 px (72 px height + 10 px gap)
    1. Vendor:           y = 125
    2. Platform:         y = 207
    3. Week Start:       y = 289
    4. ExPRT Rating:     y = 371
    5. CISA Key:         y = 453
    6. Device Exception: y = 535

Also aligns the 'Clear All Slicers' button at:
    x = 55 px, y = 1031 px, width = 220 px, height = 38 px (centered)

Backs up prior state and synchronizes into 'CS Dashboard.pbix'.
"""

import json
import os
import shutil
import time
import zipfile
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
TARGET_REP = PROJ / "CS Dashboard.Report"
PAGES_DIR = TARGET_REP / "definition" / "pages"
PBIX_PATH = BASE_DIR / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"
BACKUP_DIR = BASE_DIR / "development" / "jh_crowd_strike" / "backups"

SLICER_SPECS = [
    {"field_prop": "Vendor Normalized", "y": 125, "label": "Vendor"},
    {"field_prop": "Platform",          "y": 207, "label": "Platform"},
    {"field_prop": "Week Start",        "y": 289, "label": "Week Start"},
    {"field_prop": "ExPRT Rating",      "y": 371, "label": "ExPRT Rating"},
    {"field_prop": "is_cisa_kev",       "y": 453, "label": "CISA Key"},
    {"field_prop": "Device Patch Exception", "y": 535, "label": "Device Exception"},
]

STANDARD_X = 28
STANDARD_WIDTH = 275
STANDARD_HEIGHT = 72

CLEAR_BTN_POS = {
    "x": 55,
    "y": 1031,
    "width": 220,
    "height": 38
}

def create_backup():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"pre_slicer_uniform_align_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(PAGES_DIR, dest / "pages")
    if PBIX_PATH.exists():
        shutil.copy2(PBIX_PATH, dest / PBIX_PATH.name)
    print(f"Pre-flight backup created at: {dest}")
    return dest

def get_slicer_field_property(vdata):
    projs = vdata.get("visual", {}).get("query", {}).get("queryState", {}).get("Values", {}).get("projections", [])
    if not projs:
        return None
    field = projs[0].get("field", {})
    return field.get("Column", {}).get("Property") or field.get("Measure", {}).get("Property")

def update_page_slicers(pid):
    page_dir = PAGES_DIR / pid
    if not page_dir.exists():
        return
    pdata = json.loads((page_dir / "page.json").read_text(encoding="utf-8"))
    display_name = pdata.get("displayName", pid)
    print(f"\nProcessing page: '{display_name}' ({pid})...")

    vdir = page_dir / "visuals"
    matched_slicers = 0

    for vd in vdir.iterdir():
        vjson = vd / "visual.json"
        if not vjson.exists():
            continue
        vdata = json.loads(vjson.read_text(encoding="utf-8"))
        vtype = vdata.get("visual", {}).get("visualType")

        # 1. Align Slicers
        if vtype == "slicer":
            prop = get_slicer_field_property(vdata)
            spec = next((s for s in SLICER_SPECS if s["field_prop"] == prop), None)
            if spec:
                vdata["position"]["x"] = STANDARD_X
                vdata["position"]["y"] = spec["y"]
                vdata["position"]["width"] = STANDARD_WIDTH
                vdata["position"]["height"] = STANDARD_HEIGHT
                vjson.write_text(json.dumps(vdata, indent=2), encoding="utf-8")
                matched_slicers += 1
                print(f"  Aligned {spec['label']:20s} ({vd.name}) -> x={STANDARD_X}, y={spec['y']}, w={STANDARD_WIDTH}, h={STANDARD_HEIGHT}")
            else:
                print(f"  [Warning] Unrecognized slicer field '{prop}' in {vd.name}")

        # 2. Align Clear Button
        elif "clear" in vd.name or (vtype == "actionButton" and vdata.get("position", {}).get("y", 0) > 900):
            vdata["position"]["x"] = CLEAR_BTN_POS["x"]
            vdata["position"]["y"] = CLEAR_BTN_POS["y"]
            vdata["position"]["width"] = CLEAR_BTN_POS["width"]
            vdata["position"]["height"] = CLEAR_BTN_POS["height"]
            vjson.write_text(json.dumps(vdata, indent=2), encoding="utf-8")
            print(f"  Aligned Clear Button      ({vd.name}) -> x={CLEAR_BTN_POS['x']}, y={CLEAR_BTN_POS['y']}, w={CLEAR_BTN_POS['width']}, h={CLEAR_BTN_POS['height']}")

    print(f"  Total slicers aligned on '{display_name}': {matched_slicers}/6")

def synchronize_pbix():
    if not PBIX_PATH.exists():
        print(f"Warning: {PBIX_PATH} does not exist, skipping pbix sync.")
        return
        
    print(f"\nSynchronizing updated definition into {PBIX_PATH.name}...")
    temp_pbix = PBIX_PATH.with_suffix(".tmp.pbix")
    
    new_report_files = {}
    for root, _, files in os.walk(TARGET_REP / "definition"):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(TARGET_REP / "definition")
            archive_path = f"Report/definition/{rel_path.as_posix()}"
            with open(full_path, "rb") as fh:
                new_report_files[archive_path] = fh.read()

    if (TARGET_REP / "StaticResources").exists():
        for root, _, files in os.walk(TARGET_REP / "StaticResources"):
            for f in files:
                full_path = Path(root) / f
                rel_path = full_path.relative_to(TARGET_REP / "StaticResources")
                archive_path = f"Report/StaticResources/{rel_path.as_posix()}"
                with open(full_path, "rb") as fh:
                    new_report_files[archive_path] = fh.read()

    with zipfile.ZipFile(PBIX_PATH, "r") as zin:
        with zipfile.ZipFile(temp_pbix, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if not item.filename.startswith("Report/definition/") and not item.filename.startswith("Report/StaticResources/"):
                    zout.writestr(item, zin.read(item.filename))
            for arcname, data in new_report_files.items():
                zout.writestr(arcname, data)

    shutil.move(temp_pbix, PBIX_PATH)
    print(f"  Successfully synchronized into {PBIX_PATH.name}")

def main():
    print("=" * 65)
    print("  Aligning & Spacing Slicers Uniformly Across All Pages")
    print("=" * 65)
    create_backup()

    pages_meta = json.loads((PAGES_DIR / "pages.json").read_text(encoding="utf-8"))
    for pid in pages_meta.get("pageOrder", []):
        update_page_slicers(pid)

    synchronize_pbix()
    print("\n" + "=" * 65)
    print("  Slicer Alignment & Uniform Spacing Completed Successfully!")
    print("=" * 65)

if __name__ == "__main__":
    main()
