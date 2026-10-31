#!/usr/bin/env python3
"""
update_dynamic_chart_header.py
Implements dynamic visual title/header for 'Open Vulnerabilities Exceeding SLA' chart
and KPI card, dynamically switching to:
- "Open Vulnerabilities > 30 Days"
- "Open Vulnerabilities > 60 Days"
- "Open Vulnerabilities > 90 Days"
- "Open Vulnerabilities > 1 Year"
based on the parameter selection from the SLA Threshold dropdown.
"""

import os
import json
import zipfile
import shutil
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
SM_DIR = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard" / "CS Dashboard.SemanticModel"
REP_DIR = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard" / "CS Dashboard.Report"
PBIX_PATH = BASE_DIR / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"

def update_sla_threshold_table():
    print("--- 1. Updating 'SLA Threshold.tmdl' with clean formatted labels ---")
    sla_path = SM_DIR / "definition" / "tables" / "SLA Threshold.tmdl"
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
\t\t\t\t\t\t{ "Open Vulnerabilities > 30 Days", "Open Vulnerabilities > 30 Days", 30, 1 },
\t\t\t\t\t\t{ "Open Vulnerabilities > 60 Days", "Open Vulnerabilities > 60 Days", 60, 2 },
\t\t\t\t\t\t{ "Open Vulnerabilities > 90 Days", "Open Vulnerabilities > 90 Days", 90, 3 },
\t\t\t\t\t\t{ "Open Vulnerabilities > 1 Year", "Open Vulnerabilities > 1 Year", 365, 4 }
\t\t\t\t\t}
\t\t\t\t)
"""
    with open(sla_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  'SLA Threshold.tmdl' updated.")

def update_measures():
    print("--- 2. Updating dynamic title measures in '_Measures.tmdl' ---")
    meas_path = SM_DIR / "definition" / "tables" / "_Measures.tmdl"
    with open(meas_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Dynamic measure definition for chart and card headers
    dynamic_label_dax = """\tmeasure 'Selected SLA Label' = 
\t\t\tVAR DaysVal = [Selected SLA Days]
\t\t\tRETURN
\t\t\tSWITCH(
\t\t\t\tDaysVal,
\t\t\t\t30, "Open Vulnerabilities > 30 Days",
\t\t\t\t60, "Open Vulnerabilities > 60 Days",
\t\t\t\t90, "Open Vulnerabilities > 90 Days",
\t\t\t\t365, "Open Vulnerabilities > 1 Year",
\t\t\t\t"Open Vulnerabilities > 30 Days"
\t\t\t)
\t\tlineageTag: 12bd0804-82e3-4cd0-9a5a-bf68feb23446

\tmeasure 'Open Vulnerabilities Exceeding SLA Title' = [Selected SLA Label]
\t\tlineageTag: 7a8b9c0d-1e2f-3a4b-5c6d-7e8f9a0b1c2d"""

    # Replace existing Selected SLA Label measure
    lines = content.splitlines()
    new_lines = []
    skip_until_blank = False
    replaced = False

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("measure 'Selected SLA Label'"):
            # skip this and its properties
            while i < len(lines) and lines[i].strip() != "" and not lines[i].strip().startswith("measure '"):
                i += 1
            new_lines.append(dynamic_label_dax)
            replaced = True
            continue
        elif line.strip().startswith("measure 'Open Vulnerabilities Exceeding SLA Title'"):
            # skip existing if present
            while i < len(lines) and lines[i].strip() != "" and not lines[i].strip().startswith("measure '"):
                i += 1
            continue
        new_lines.append(line)
        i += 1

    if not replaced:
        new_lines.append("\n" + dynamic_label_dax)

    with open(meas_path, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")
    print("  '_Measures.tmdl' updated with dynamic 'Selected SLA Label' and 'Open Vulnerabilities Exceeding SLA Title'.")

def update_visual_titles():
    print("--- 3. Configuring dynamic title in chart & KPI visual definitions ---")
    p1_vis_dir = REP_DIR / "definition" / "pages" / "47081098f92a957d7fd0" / "visuals"

    # 1. Aging bar chart (v11_aging_barchart0)
    chart_file = p1_vis_dir / "v11_aging_barchart0" / "visual.json"
    if chart_file.exists():
        with open(chart_file, "r", encoding="utf-8") as f:
            cdef = json.load(f)
        
        cdef.setdefault("visual", {}).setdefault("visualContainerObjects", {})["title"] = [
            {
                "properties": {
                    "show": {
                        "expr": {
                            "Literal": {
                                "Value": "true"
                            }
                        }
                    },
                    "text": {
                        "expr": {
                            "Measure": {
                                "Expression": {
                                    "SourceRef": {
                                        "Entity": "_Measures"
                                    }
                                },
                                "Property": "Selected SLA Label"
                            }
                        }
                    },
                    "titleWrap": {
                        "expr": {
                            "Literal": {
                                "Value": "true"
                            }
                        }
                    }
                }
            }
        ]
        with open(chart_file, "w", encoding="utf-8") as f:
            json.dump(cdef, f, indent=2)
        print("  Configured dynamic title on chart 'v11_aging_barchart0'.")

    # 2. KPI Card (v06_kpi_openover30d)
    kpi_file = p1_vis_dir / "v06_kpi_openover30d" / "visual.json"
    if kpi_file.exists():
        with open(kpi_file, "r", encoding="utf-8") as f:
            kdef = json.load(f)
        
        kdef.setdefault("visual", {}).setdefault("visualContainerObjects", {})["title"] = [
            {
                "properties": {
                    "show": {
                        "expr": {
                            "Literal": {
                                "Value": "true"
                            }
                        }
                    },
                    "text": {
                        "expr": {
                            "Measure": {
                                "Expression": {
                                    "SourceRef": {
                                        "Entity": "_Measures"
                                    }
                                },
                                "Property": "Selected SLA Label"
                            }
                        }
                    },
                    "titleWrap": {
                        "expr": {
                            "Literal": {
                                "Value": "true"
                            }
                        }
                    }
                }
            }
        ]
        with open(kpi_file, "w", encoding="utf-8") as f:
            json.dump(kdef, f, indent=2)
        print("  Configured dynamic title on KPI card 'v06_kpi_openover30d'.")

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
    print("  Applying Dynamic Chart & KPI Header Driven by SLA Parameter")
    print("=========================================================")
    update_sla_threshold_table()
    update_measures()
    update_visual_titles()
    synchronize_pbix()
    print("=========================================================")
    print("  Dynamic Chart Header Configured Successfully!")
    print("=========================================================")

if __name__ == "__main__":
    main()
