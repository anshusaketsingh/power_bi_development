"""
update_sla_threshold_feature.py
Adds dynamic SLA threshold selection (>30 Days, >60 Days, >90 Days, >1 Year):
1. Creates 'SLA Threshold.tmdl' calculated table.
2. Refines 'Age Bucket' in crowdstrike_vulnerability_device_reporting.tmdl to include '>1 Year'.
3. Adds dynamic measures:
   - [Selected SLA Days]
   - [Selected SLA Label]
   - [Open Vulnerabilities Exceeding SLA]
   - [Open Vulnerabilities by SLA Bucket]
4. Updates model.tmdl with ref table 'SLA Threshold'.
5. Updates report visuals:
   - Adds v13_slicer_sla_thresh (Dropdown slicer)
   - Re-binds KPI Card v06_kpi_openover30d to [Open Vulnerabilities Exceeding SLA]
   - Re-binds Aging Chart v11_aging_barchart0 to [Open Vulnerabilities by SLA Bucket]
6. Synchronizes changes into CS Dashboard.pbix archive.
"""

import os
import json
import re
from pathlib import Path

BASE_DIR = Path("development/jh_crowd_strike/CS_Dashboard")
SEM_DIR = BASE_DIR / "CS Dashboard.SemanticModel"
REP_DIR = BASE_DIR / "CS Dashboard.Report"
DEF_DIR = SEM_DIR / "definition"
TABLES_DIR = DEF_DIR / "tables"
PBIX_PATH = Path("development/jh_crowd_strike/CS Dashboard.pbix")

def update_semantic_model():
    print("1. Updating Semantic Model for Dynamic SLA Thresholds...")

    # A. Create SLA Threshold.tmdl
    sla_table_tmdl = """table 'SLA Threshold'

\tcolumn 'SLA Threshold'
\t\tdataType: string
\t\tsortByColumn: 'Sort Order'
\t\tsourceColumn: [SLA Threshold]

\tcolumn 'Threshold Days'
\t\tdataType: int64
\t\tisHidden
\t\tsummarizeBy: none
\t\tsourceColumn: [Threshold Days]

\tcolumn 'Sort Order'
\t\tdataType: int64
\t\tisHidden
\t\tsummarizeBy: none
\t\tsourceColumn: [Sort Order]

\tpartition 'SLA Threshold' = calculated
\t\tmode: import
\t\tsource = ```
\t\t\tDATATABLE(
\t\t\t\t"SLA Threshold", STRING,
\t\t\t\t"Threshold Days", INTEGER,
\t\t\t\t"Sort Order", INTEGER,
\t\t\t\t{
\t\t\t\t\t{ "Open Vulnerabilities >30 Days", 30, 1 },
\t\t\t\t\t{ "Open Vulnerabilities >60 Days", 60, 2 },
\t\t\t\t\t{ "Open Vulnerabilities >90 Days", 90, 3 },
\t\t\t\t\t{ "Open Vulnerabilities >1 Year", 365, 4 }
\t\t\t\t}
\t\t\t)
\t\t\t```
"""
    with open(TABLES_DIR / "SLA Threshold.tmdl", "w", encoding="utf-8") as f:
        f.write(sla_table_tmdl)
    print("Created SLA Threshold.tmdl")

    # B. Update crowdstrike_vulnerability_device_reporting.tmdl to refine Age Bucket
    main_table_file = TABLES_DIR / "crowdstrike_vulnerability_device_reporting.tmdl"
    with open(main_table_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Refine Age Bucket to segment >1 Year
    new_age_bucket = """\tcolumn 'Age Bucket' =
\t\t\tSWITCH(
\t\t\t\tTRUE(),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] <> "Open", "Closed",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 30, "0-30 Days",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 60, "31-60 Days",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 90, "61-90 Days",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 365, "91-365 Days",
\t\t\t\t">1 Year"
\t\t\t)
\t\tdataType: string
\t\tsortByColumn: 'Age Bucket Sort'
\t\tsummarizeBy: none

\tcolumn 'Age Bucket Sort' =
\t\t\tSWITCH(
\t\t\t\tTRUE(),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] <> "Open", 0,
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 30, 1,
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 60, 2,
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 90, 3,
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 365, 4,
\t\t\t\t5
\t\t\t)
\t\tdataType: int64
\t\tisHidden
\t\tsummarizeBy: none"""

    # Replace old Age Bucket definition if present
    content = re.sub(
        r"\tcolumn 'Age Bucket' =[\s\S]*?dataType: string\s*\n\t\tsummarizeBy: none",
        new_age_bucket,
        content
    )
    with open(main_table_file, "w", encoding="utf-8") as f:
        f.write(content)
    print("Refined Age Bucket in crowdstrike_vulnerability_device_reporting.tmdl")

    # C. Update _Measures.tmdl with dynamic threshold measures
    measures_file = TABLES_DIR / "_Measures.tmdl"
    with open(measures_file, "r", encoding="utf-8") as f:
        meas_content = f.read()

    new_measures = """
\tmeasure 'Selected SLA Days' = ```
\t\tSELECTEDVALUE('SLA Threshold'[Threshold Days], 30)
\t\t```
\t\tformatString: 0

\tmeasure 'Selected SLA Label' = ```
\t\tSELECTEDVALUE('SLA Threshold'[SLA Threshold], "Open Vulnerabilities >30 Days")
\t\t```

\tmeasure 'Open Vulnerabilities Exceeding SLA' = ```
\t\t// Dynamically counts open findings older than selected SLA threshold
\t\tVAR ThresholdDays = [Selected SLA Days]
\t\tVAR CutoffDate = TODAY() - ThresholdDays
\t\tRETURN
\t\tCALCULATE(
\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Created Date] <= CutoffDate
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'Open Vulnerabilities by SLA Bucket' = ```
\t\t// Dynamically filters aging buckets based on selected SLA threshold
\t\tVAR ThresholdDays = [Selected SLA Days]
\t\tVAR CurrentBucket = SELECTEDVALUE('crowdstrike_vulnerability_device_reporting'[Age Bucket])
\t\tVAR BucketMaxDays = 
\t\t\tSWITCH(
\t\t\t\tCurrentBucket,
\t\t\t\t"0-30 Days", 30,
\t\t\t\t"31-60 Days", 60,
\t\t\t\t"61-90 Days", 90,
\t\t\t\t"91-365 Days", 365,
\t\t\t\t">1 Year", 99999,
\t\t\t\tBLANK()
\t\t\t)
\t\tRETURN
\t\tIF(
\t\t\tNOT(ISBLANK(BucketMaxDays)) && BucketMaxDays >= ThresholdDays,
\t\t\t[Open Vulnerabilities],
\t\t\tBLANK()
\t\t)
\t\t```
\t\tformatString: #,##0
"""
    if "Open Vulnerabilities Exceeding SLA" not in meas_content:
        part_idx = meas_content.find("\tcolumn Dummy")
        if part_idx != -1:
            meas_content = meas_content[:part_idx] + new_measures + "\n" + meas_content[part_idx:]
        else:
            meas_content = meas_content + "\n" + new_measures
        with open(measures_file, "w", encoding="utf-8") as f:
            f.write(meas_content)
        print("Added SLA threshold measures to _Measures.tmdl")

    # D. Update model.tmdl to reference 'SLA Threshold'
    model_file = DEF_DIR / "model.tmdl"
    with open(model_file, "r", encoding="utf-8") as f:
        model_content = f.read()
    if "ref table 'SLA Threshold'" not in model_content and "ref table SLA Threshold" not in model_content:
        pos = model_content.find("ref cultureInfo")
        ref_line = "ref table 'SLA Threshold'\n\n"
        if pos != -1:
            model_content = model_content[:pos] + ref_line + model_content[pos:]
        else:
            model_content = model_content + "\n" + ref_line
        with open(model_file, "w", encoding="utf-8") as f:
            f.write(model_content)
        print("Updated model.tmdl with ref table 'SLA Threshold'")


def update_report_visuals():
    print("2. Updating Report Visuals with SLA Threshold Dropdown...")
    pages_dir = REP_DIR / "definition" / "pages"
    pages_json_file = pages_dir / "pages.json"
    with open(pages_json_file, "r", encoding="utf-8") as f:
        pages_meta = json.load(f)

    active_page_id = pages_meta.get("activePageName") or pages_meta["pageOrder"][0]
    page_dir = pages_dir / active_page_id
    vis_dir = page_dir / "visuals"
    vis_dir.mkdir(parents=True, exist_ok=True)

    def write_vis(v_id: str, obj: dict):
        p = vis_dir / v_id
        p.mkdir(parents=True, exist_ok=True)
        with open(p / "visual.json", "w", encoding="utf-8") as vf:
            json.dump(obj, vf, indent=2)

    # 1. Update Title visual width to make room for 4 top slicers
    write_vis("v01_banner_title000", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v01_banner_title000",
        "position": {"x": 30, "y": 20, "z": 100, "height": 70, "width": 860, "tabOrder": 1},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [
                                {
                                    "value": "CrowdStrike Windows Vulnerability & Patch Compliance",
                                    "textStyle": {"fontFamily": "Segoe UI", "fontSize": "22pt", "fontWeight": "bold", "color": {"solid": {"color": "#0F172A"}}}
                                },
                                {
                                    "value": "\nExecutive Board Reporting | Scope: Microsoft Windows Only",
                                    "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "fontWeight": "normal", "color": {"solid": {"color": "#64748B"}}}
                                }
                            ]
                        }]
                    }
                }]
            }
        }
    })

    # 2. Adjust Platform Slicer position
    write_vis("v02_slicer_platform0", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v02_slicer_platform0",
        "position": {"x": 910, "y": 20, "z": 200, "height": 70, "width": 220, "tabOrder": 2},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "Platform"}},
                            "queryRef": "crowdstrike_vulnerability_device_reporting.Platform",
                            "nativeQueryRef": "Platform"
                        }]
                    }
                }
            }
        }
    })

    # 3. Scope Slicer (Vendor Normalized)
    write_vis("v03_slicer_vendor000", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v03_slicer_vendor000",
        "position": {"x": 1150, "y": 20, "z": 300, "height": 70, "width": 220, "tabOrder": 3},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "Vendor Normalized"}},
                            "queryRef": "crowdstrike_vulnerability_device_reporting.Vendor Normalized",
                            "nativeQueryRef": "Vendor Normalized"
                        }]
                    }
                }
            }
        }
    })

    # 4. Week Slicer
    write_vis("v04_slicer_weekstart", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v04_slicer_weekstart",
        "position": {"x": 1390, "y": 20, "z": 400, "height": 70, "width": 230, "tabOrder": 4},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Calendar"}}, "Property": "Week Start"}},
                            "queryRef": "Calendar.Week Start",
                            "nativeQueryRef": "Week Start"
                        }]
                    }
                }
            }
        }
    })

    # 5. NEW: SLA Threshold Dropdown Slicer
    write_vis("v13_slicer_sla_thresh", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v13_slicer_sla_thresh",
        "position": {"x": 1640, "y": 20, "z": 450, "height": 70, "width": 250, "tabOrder": 5},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "SLA Threshold"}}, "Property": "SLA Threshold"}},
                            "queryRef": "SLA Threshold.SLA Threshold",
                            "nativeQueryRef": "SLA Threshold"
                        }]
                    }
                }
            }
        }
    })

    # 6. UPDATE: Dynamic SLA Breach KPI Card (v06_kpi_openover30d)
    write_vis("v06_kpi_openover30d", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v06_kpi_openover30d",
        "position": {"x": 406, "y": 110, "z": 500, "height": 130, "width": 356, "tabOrder": 6},
        "visual": {
            "visualType": "cardVisual",
            "query": {
                "queryState": {
                    "Data": {
                        "projections": [{
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Open Vulnerabilities Exceeding SLA"}},
                            "queryRef": "_Measures.Open Vulnerabilities Exceeding SLA",
                            "nativeQueryRef": "Open Vulnerabilities Exceeding SLA"
                        }]
                    }
                }
            }
        }
    })

    # 7. UPDATE: Dynamic Aging Chart responding directly to SLA Threshold selection (v11_aging_barchart0)
    write_vis("v11_aging_barchart0", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v11_aging_barchart0",
        "position": {"x": 1200, "y": 260, "z": 700, "height": 410, "width": 690, "tabOrder": 11},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "Age Bucket"}},
                            "queryRef": "crowdstrike_vulnerability_device_reporting.Age Bucket",
                            "nativeQueryRef": "Age Bucket"
                        }]
                    },
                    "Y": {
                        "projections": [{
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Open Vulnerabilities by SLA Bucket"}},
                            "queryRef": "_Measures.Open Vulnerabilities by SLA Bucket",
                            "nativeQueryRef": "Open Vulnerabilities by SLA Bucket"
                        }]
                    }
                }
            }
        }
    })
    print("Updated report visuals with SLA threshold dropdown and bound dynamic measures.")


def update_pbix_archive():
    if not PBIX_PATH.exists():
        return
    import zipfile, shutil
    temp_pbix = PBIX_PATH.with_suffix(".tmp.pbix")
    def_prefix = "Report/definition/"
    
    new_files = {}
    for root, _, files in os.walk(REP_DIR / "definition"):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(REP_DIR / "definition")
            archive_path = f"Report/definition/{rel_path.as_posix()}"
            with open(full_path, "rb") as fh:
                new_files[archive_path] = fh.read()

    with zipfile.ZipFile(PBIX_PATH, "r") as zin:
        with zipfile.ZipFile(temp_pbix, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if not item.filename.startswith(def_prefix):
                    zout.writestr(item, zin.read(item.filename))
            for arcname, data in new_files.items():
                zout.writestr(arcname, data)

    shutil.move(temp_pbix, PBIX_PATH)
    print(f"Synchronized PBIX archive {PBIX_PATH} with {len(new_files)} report definitions.")


def main():
    print("=== Implementing Dynamic SLA Threshold Dropdown & Reactive Chart ===")
    update_semantic_model()
    update_report_visuals()
    update_pbix_archive()
    print("All tasks completed successfully!")

if __name__ == "__main__":
    main()
