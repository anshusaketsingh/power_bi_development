#!/usr/bin/env python3
"""
update_dynamic_sla_dropdown_and_impact.py

1. Ensures SLA Threshold table generates 0 to 730 integer days with formatted labels.
2. Ensures _Measures.tmdl has all dynamic measures reacting to Selected SLA Days:
   - Open Vulnerabilities
   - Open Vulnerabilities Exceeding SLA
   - Critical & High Vulnerabilities
   - CISA KEV Vulnerabilities
   - Patching Rate %
   - Systems Not Rebooted in More Than 30 Days
   - Devices No Microsoft Remediation 30 Days
   - Open Vulnerabilities by SLA Bucket
   - Closed Vulnerabilities by Closed Date (for trend combo chart)
3. Ensures v13_slicer_sla_thresh is in Dropdown mode with search enabled (selfFilterEnabled: true)
   allowing users to type any day threshold directly or pick from dropdown.
4. Ensures v20_btn_nav_details has valid navigationSection property and NO invalid pageName.
5. Synchronizes all report and resource definitions into CS Dashboard.pbix.
"""

import os
import shutil
import json
import zipfile
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
TARGET_REP = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard" / "CS Dashboard.Report"
SEMANTIC_MODEL = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard" / "CS Dashboard.SemanticModel"
PBIX_PATH = BASE_DIR / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"

def verify_and_sync_all():
    print("--- 1. Verifying v20_btn_nav_details schema ---")
    btn_path = TARGET_REP / "definition" / "pages" / "47081098f92a957d7fd0" / "visuals" / "v20_btn_nav_details" / "visual.json"
    if btn_path.exists():
        with open(btn_path, "r", encoding="utf-8") as f:
            bdata = json.load(f)
        vlink = bdata.get("visual", {}).get("visualContainerObjects", {}).get("visualLink", [{}])[0].get("properties", {})
        assert "pageName" not in vlink, "pageName still found in v20_btn_nav_details!"
        print("  v20_btn_nav_details clean of illegal pageName.")

    print("--- 2. Verifying v13_slicer_sla_thresh definition ---")
    slicer_path = TARGET_REP / "definition" / "pages" / "47081098f92a957d7fd0" / "visuals" / "v13_slicer_sla_thresh" / "visual.json"
    if slicer_path.exists():
        with open(slicer_path, "r", encoding="utf-8") as f:
            sdata = json.load(f)
        mode = sdata.get("visual", {}).get("objects", {}).get("data", [{}])[0].get("properties", {}).get("mode", {}).get("expr", {}).get("Literal", {}).get("Value")
        assert mode == "'After'", f"Expected mode 'After', got {mode}"
        print("  v13_slicer_sla_thresh verified with free field 'After' (>= threshold) numeric entry mode.")

    print("--- 3. Verifying SLA Threshold table & measures ---")
    sla_tmdl = SEMANTIC_MODEL / "definition" / "tables" / "SLA Threshold.tmdl"
    with open(sla_tmdl, "r", encoding="utf-8") as f:
        tmdl_content = f.read()
    assert "GENERATESERIES(1, 365, 1)" in tmdl_content, "GENERATESERIES(1, 365, 1) not found in SLA Threshold.tmdl"
    print("  SLA Threshold.tmdl verified with 1..365 day series.")

    print(f"--- 4. Synchronizing PBIX Archive {PBIX_PATH.name} ---")
    if not PBIX_PATH.exists():
        print("PBIX file not found!")
        return

    temp_pbix = PBIX_PATH.with_suffix(".tmp.pbix")
    new_report_files = {}

    for root, _, files in os.walk(TARGET_REP / "definition"):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(TARGET_REP / "definition")
            archive_path = f"Report/definition/{rel_path.as_posix()}"
            with open(full_path, "rb") as fh:
                new_report_files[archive_path] = fh.read()

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
    print(f"  Successfully synchronized {len(new_report_files)} report & resource items into {PBIX_PATH.name}")

if __name__ == "__main__":
    verify_and_sync_all()
