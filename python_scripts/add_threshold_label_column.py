#!/usr/bin/env python3
"""
add_threshold_label_column.py
Ensures 'Threshold Label' is explicitly defined as a first-class column in the 'SLA Threshold'
table within the Semantic Model, so that it appears clearly in Power BI Desktop's Fields list
and binds correctly to slicers and dynamic measures.

Both 'Threshold Label' and 'SLA Threshold' columns are provided for full backward and forward
compatibility across DAX measures and visuals.
"""

import os
import shutil
import json
import zipfile
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
SM_DIR = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard" / "CS Dashboard.SemanticModel"
REP_DIR = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard" / "CS Dashboard.Report"
PBIX_PATH = BASE_DIR / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"

def update_sla_threshold_table():
    print("--- 1. Updating 'SLA Threshold.tmdl' to include 'Threshold Label' column ---")
    sla_tmdl_path = SM_DIR / "definition" / "tables" / "SLA Threshold.tmdl"
    
    content = """table 'SLA Threshold'
\tlineageTag: 29ccbaa5-5811-408b-a961-bea13ade3e8f

\tcolumn 'Threshold Label'
\t\tdataType: string
\t\tlineageTag: 2612d13b-fb20-4e0b-9e4b-654c7f6e0a10
\t\tsourceColumn: [Threshold Label]
\t\tsortByColumn: 'Sort Order'

\tcolumn 'SLA Threshold'
\t\tdataType: string
\t\tlineageTag: a3b4c5d6-e7f8-4901-8234-56789abcdef0
\t\tsourceColumn: [SLA Threshold]
\t\tsortByColumn: 'Sort Order'

\tcolumn 'Threshold Days'
\t\tdataType: int64
\t\tisHidden
\t\tlineageTag: dd153c8a-1442-4abd-a444-1a2d68c2f7bf
\t\tsummarizeBy: none
\t\tsourceColumn: [Threshold Days]

\tcolumn 'Sort Order'
\t\tdataType: int64
\t\tisHidden
\t\tlineageTag: cea69ef7-c5c6-4360-90ee-bf4300fe744c
\t\tsummarizeBy: none
\t\tsourceColumn: [Sort Order]

\tpartition 'SLA Threshold' = calculated
\t\tmode: import
\t\tsource =
\t\t\t\tDATATABLE(
\t\t\t\t\t"Threshold Label", STRING,
\t\t\t\t\t"SLA Threshold", STRING,
\t\t\t\t\t"Threshold Days", INTEGER,
\t\t\t\t\t"Sort Order", INTEGER,
\t\t\t\t\t{
\t\t\t\t\t\t{ "Open Vulnerabilities >30 Days", "Open Vulnerabilities >30 Days", 30, 1 },
\t\t\t\t\t\t{ "Open Vulnerabilities >60 Days", "Open Vulnerabilities >60 Days", 60, 2 },
\t\t\t\t\t\t{ "Open Vulnerabilities >90 Days", "Open Vulnerabilities >90 Days", 90, 3 },
\t\t\t\t\t\t{ "Open Vulnerabilities >1 Year", "Open Vulnerabilities >1 Year", 365, 4 }
\t\t\t\t\t}
\t\t\t\t)
"""
    with open(sla_tmdl_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  'SLA Threshold.tmdl' updated with 'Threshold Label' and 'SLA Threshold' columns.")

def update_measures():
    print("--- 2. Updating 'Selected SLA Label' measure in '_Measures.tmdl' ---")
    meas_path = SM_DIR / "definition" / "tables" / "_Measures.tmdl"
    with open(meas_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Ensure Selected SLA Label gracefully accepts both Threshold Label and SLA Threshold
    old_def = 'measure \'Selected SLA Label\' = SELECTEDVALUE(\'SLA Threshold\'[SLA Threshold], "Open Vulnerabilities >30 Days")'
    new_def = 'measure \'Selected SLA Label\' = COALESCE(SELECTEDVALUE(\'SLA Threshold\'[Threshold Label]), SELECTEDVALUE(\'SLA Threshold\'[SLA Threshold]), "Open Vulnerabilities >30 Days")'
    
    if old_def in content:
        content = content.replace(old_def, new_def)
    elif "measure 'Selected SLA Label'" not in content:
        # append if not present
        content += f"\n\n\t{new_def}\n\t\tlineageTag: 12bd0804-82e3-4cd0-9a5a-bf68feb23446\n"
    else:
        # replace any singleline Selected SLA Label measure
        lines = content.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("measure 'Selected SLA Label'"):
                lines[i] = f"\t{new_def}"
                break
        content = "\n".join(lines)

    with open(meas_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  '_Measures.tmdl' verified.")

def update_slicer_visual():
    print("--- 3. Verifying 'v13_slicer_sla_thresh' visual definition ---")
    slicer_dir = REP_DIR / "definition" / "pages" / "47081098f92a957d7fd0" / "visuals" / "v13_slicer_sla_thresh"
    slicer_file = slicer_dir / "visual.json"
    
    if slicer_file.exists():
        with open(slicer_file, "r", encoding="utf-8") as f:
            sdef = json.load(f)
        
        # Verify projections
        sdef["visual"]["query"]["queryState"]["Values"]["projections"] = [
            {
                "field": {
                    "Column": {
                        "Expression": {
                            "SourceRef": {
                                "Entity": "SLA Threshold"
                            }
                        },
                        "Property": "Threshold Label"
                    }
                },
                "queryRef": "SLA Threshold.Threshold Label",
                "nativeQueryRef": "Threshold Label",
                "active": True
            }
        ]
        with open(slicer_file, "w", encoding="utf-8") as f:
            json.dump(sdef, f, indent=2)
        print("  'v13_slicer_sla_thresh' verified and bound to 'SLA Threshold'[Threshold Label].")

def synchronize_pbix():
    print(f"--- 4. Synchronizing PBIX Archive {PBIX_PATH.name} ---")
    if not PBIX_PATH.exists():
        return

    temp_pbix = PBIX_PATH.with_suffix(".tmp.pbix")
    
    new_report_files = {}
    for root, _, files in os.walk(REP_DIR / "definition"):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(REP_DIR / "definition")
            archive_path = f"Report/definition/{rel_path.as_posix()}"
            with open(full_path, "rb") as fh:
                new_report_files[archive_path] = fh.read()

    for root, _, files in os.walk(REP_DIR / "StaticResources"):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(REP_DIR / "StaticResources")
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

def main():
    print("=========================================================")
    print("  Adding 'Threshold Label' to Semantic Model & Visuals")
    print("=========================================================")
    update_sla_threshold_table()
    update_measures()
    update_slicer_visual()
    synchronize_pbix()
    print("=========================================================")
    print("  'Threshold Label' is now available in Semantic Model!")
    print("=========================================================")

if __name__ == "__main__":
    main()
