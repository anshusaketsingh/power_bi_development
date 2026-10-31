#!/usr/bin/env python3
"""
apply_executive_slicers_to_all_tabs.py

Copies the exact slicers and formatting from Executive Summary (47081098f92a957d7fd0)
to the rest of the dashboard tabs:
- Trends & Device Exceptions (p02_trends_exceptions)
- Vulnerability Overview (p04_vulnerability_overview)
- Remediation Compliance (p03_vulnerability_details)
- Vulnerability Details (p05_vulnerability_details)

The 6 slicers applied in exact Executive Summary format and order:
1. Vendor (Vendor Normalized, DisplayName: "Vendor")
2. Platform (Platform, Dropdown inverted mode)
3. Week Start (Calendar.Week Start)
4. ExPRT Rating (ExPRT Rating, with ExPRT Rating sync group)
5. CISA Key (is_cisa_kev, DisplayName: "CISA Key", filter: false/true)
6. Device Exception (Device Patch Exception, DisplayName: "Device Exception")

Also ensures the "Clear All Slicers" button on each tab matches Executive Summary.
Backs up prior state and synchronizes changes into 'CS Dashboard.pbix'.
"""

import json
import os
import shutil
import time
import uuid
import zipfile
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
PAGES_DIR = PROJ / "CS Dashboard.Report" / "definition" / "pages"
TARGET_REP = PROJ / "CS Dashboard.Report"
PBIX_PATH = BASE_DIR / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"
BACKUP_DIR = BASE_DIR / "development" / "jh_crowd_strike" / "backups"

EXEC_PAGE_ID = "47081098f92a957d7fd0"
TARGET_PAGES = [
    ("p02_trends_exceptions", "p2", "Trends & Device Exceptions"),
    ("p04_vulnerability_overview", "p4", "Vulnerability Overview"),
    ("p03_vulnerability_details", "p3", "Remediation Compliance"),
    ("p05_vulnerability_details", "p5", "Vulnerability Details"),
]

# Slicer template folders on Executive Summary in top-to-bottom order
EXEC_SLICER_TEMPLATES = [
    ("vendor", "v03_slicer_vendor000"),
    ("platform", "v02_slicer_platform0"),
    ("week", "v04_slicer_weekstart"),
    ("exprt", "f3f1dfac8913816f8053"),
    ("cisakev", "v16_slicer_cisakev"),
    ("devexcept", "v17_slicer_devexcept"),
]

def create_backup():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"pre_exec_slicers_sync_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    
    # Backup pages
    shutil.copytree(PAGES_DIR, dest / "pages")
    
    # Backup pbix if exists
    if PBIX_PATH.exists():
        shutil.copy2(PBIX_PATH, dest / PBIX_PATH.name)
        
    print(f"Backup created at: {dest}")
    return dest

def synchronize_pbix():
    if not PBIX_PATH.exists():
        print(f"Warning: {PBIX_PATH} does not exist, skipping pbix sync.")
        return
        
    print(f"Synchronizing PBIP definition into {PBIX_PATH.name}...")
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

def load_exec_templates():
    exec_visuals_dir = PAGES_DIR / EXEC_PAGE_ID / "visuals"
    templates = []
    for key, folder_name in EXEC_SLICER_TEMPLATES:
        vjson_path = exec_visuals_dir / folder_name / "visual.json"
        if not vjson_path.exists():
            raise FileNotFoundError(f"Template visual {vjson_path} not found!")
        data = json.loads(vjson_path.read_text(encoding="utf-8"))
        templates.append((key, data))
        
    # Also load clear button template
    clear_btn_path = exec_visuals_dir / "v_btn_clear_slicers" / "visual.json"
    clear_btn_data = json.loads(clear_btn_path.read_text(encoding="utf-8")) if clear_btn_path.exists() else None
    
    return templates, clear_btn_data

def apply_slicers_to_page(page_id, prefix, display_name, templates, clear_btn_template):
    page_visuals_dir = PAGES_DIR / page_id / "visuals"
    if not page_visuals_dir.exists():
        print(f"Skipping {page_id}: visuals directory not found.")
        return

    print(f"\nProcessing tab: '{display_name}' ({page_id})...")

    # 1. Identify and remove existing slicer visuals on this page
    existing_slicers_removed = []
    for vd in list(page_visuals_dir.iterdir()):
        vjson = vd / "visual.json"
        if not vjson.exists():
            continue
        try:
            vdata = json.loads(vjson.read_text(encoding="utf-8"))
        except Exception:
            continue
        if vdata.get("visual", {}).get("visualType") == "slicer":
            shutil.rmtree(vd)
            existing_slicers_removed.append(vd.name)
            
    print(f"  Removed old slicers ({len(existing_slicers_removed)}): {existing_slicers_removed}")

    # 2. Add the 6 standardized slicers from Executive Summary
    for key, tmpl in templates:
        new_visual = json.loads(json.dumps(tmpl))  # deep copy
        new_folder_name = f"{prefix}_slicer_{key}"
        new_visual["name"] = new_folder_name

        # Regenerate unique filter name in filterConfig
        if "filterConfig" in new_visual and "filters" in new_visual["filterConfig"]:
            for f in new_visual["filterConfig"]["filters"]:
                f["name"] = uuid.uuid4().hex[:20]

        target_dir = page_visuals_dir / new_folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "visual.json").write_text(json.dumps(new_visual, indent=2), encoding="utf-8")
        print(f"  Created slicer: {new_folder_name} (y={new_visual.get('position', {}).get('y'):.1f})")

    # 3. Standardize the Clear All Slicers button
    if clear_btn_template:
        # Find clear button on this page
        btn_folder_name = None
        for vd in page_visuals_dir.iterdir():
            if "clear" in vd.name:
                btn_folder_name = vd.name
                break
                
        if not btn_folder_name:
            btn_folder_name = f"{prefix}_btn_clear_slicers"
            
        target_btn_dir = page_visuals_dir / btn_folder_name
        target_btn_dir.mkdir(parents=True, exist_ok=True)
        
        btn_data = json.loads(json.dumps(clear_btn_template))
        btn_data["name"] = btn_folder_name
        (target_btn_dir / "visual.json").write_text(json.dumps(btn_data, indent=2), encoding="utf-8")
        print(f"  Updated clear button: {btn_folder_name} at y={btn_data.get('position', {}).get('y'):.1f}")

def main():
    print("=" * 65)
    print("  Applying Executive Summary Slicers & Format to All Dashboard Tabs")
    print("=" * 65)
    
    # 1. Pre-flight backup
    create_backup()
    
    # 2. Load templates from Executive Summary
    templates, clear_btn_template = load_exec_templates()
    print(f"Loaded {len(templates)} slicer templates and clear button from Executive Summary.")
    
    # 3. Apply to each target page
    for page_id, prefix, display_name in TARGET_PAGES:
        apply_slicers_to_page(page_id, prefix, display_name, templates, clear_btn_template)
        
    # 4. Synchronize into .pbix
    synchronize_pbix()
    
    print("\n" + "=" * 65)
    print("  Slicer Synchronization Completed Successfully!")
    print("=" * 65)

if __name__ == "__main__":
    main()
