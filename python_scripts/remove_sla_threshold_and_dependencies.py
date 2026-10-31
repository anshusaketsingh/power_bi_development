"""
remove_sla_threshold_and_dependencies.py

Completely removes SLA Threshold table and all its dependencies:
1. Deletes 'SLA Threshold.tmdl' and removes its reference from 'model.tmdl'.
2. Removes 'SLA Threshold' node from 'diagramLayout.json'.
3. Removes the 4 SLA Threshold slicers:
   - 47081098f92a957d7fd0/v13_slicer_sla_thresh
   - p02_trends_exceptions/p2_v13_slicer_sla_thresh
   - p03_vulnerability_details/p3_v13_slicer_sla_thresh
   - p05_vulnerability_details/p5_v13_slicer_sla_thresh
4. Removes scratch Page 4 (50766f0da259202948c2) which tested SLA Threshold.
5. Updates _Measures.tmdl:
   - Removes [Selected SLA Days], [Selected SLA Label], [Open Vulnerabilities Exceeding SLA].
   - Restores [Open Vulnerabilities], [Critical & High], [CISA KEV], [Patching Rate %],
     [Closed Vulnerabilities by Closed Date], and aging bucket measures to standard definitions.
6. Replaces dynamic title bindings in Executive Summary:
   - v06_kpi_openover30d: static title 'Open Vulnerabilities > 30 Days', projects [Open Vulnerabilities >30 Days]
   - v11_aging_barchart0: static title 'Open Vulnerabilities by Aging Bucket'
"""

import json
import shutil
import time
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
SEMANTIC_MODEL = PROJ / "CS Dashboard.SemanticModel" / "definition"
TABLES_DIR = SEMANTIC_MODEL / "tables"
SLA_TMDL = TABLES_DIR / "SLA Threshold.tmdl"
MODEL_TMDL = SEMANTIC_MODEL / "model.tmdl"
DIAGRAM_JSON = PROJ / "CS Dashboard.SemanticModel" / "diagramLayout.json"
MEASURES_TMDL = TABLES_DIR / "_Measures.tmdl"
REPORT_PAGES = PROJ / "CS Dashboard.Report" / "definition" / "pages"
PAGES_JSON = REPORT_PAGES / "pages.json"

SLICER_DIRS = [
    REPORT_PAGES / "47081098f92a957d7fd0" / "visuals" / "v13_slicer_sla_thresh",
    REPORT_PAGES / "p02_trends_exceptions" / "visuals" / "p2_v13_slicer_sla_thresh",
    REPORT_PAGES / "p03_vulnerability_details" / "visuals" / "p3_v13_slicer_sla_thresh",
    REPORT_PAGES / "p05_vulnerability_details" / "visuals" / "p5_v13_slicer_sla_thresh"
]

SCRATCH_PAGE4 = REPORT_PAGES / "50766f0da259202948c2"

def backup():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BASE_DIR / "development" / "jh_crowd_strike" / "backups" / f"pre_sla_threshold_removal_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    if SLA_TMDL.exists():
        shutil.copy2(SLA_TMDL, dest / "SLA Threshold.tmdl")
    if MODEL_TMDL.exists():
        shutil.copy2(MODEL_TMDL, dest / "model.tmdl")
    if MEASURES_TMDL.exists():
        shutil.copy2(MEASURES_TMDL, dest / "_Measures.tmdl")
    if PAGES_JSON.exists():
        shutil.copy2(PAGES_JSON, dest / "pages.json")
    print(f"Pre-flight backup saved at: {dest}")

def delete_sla_table():
    print("--- 1. Deleting SLA Threshold table and references ---")
    if SLA_TMDL.exists():
        SLA_TMDL.unlink()
        print("  + Deleted SLA Threshold.tmdl")
        
    if MODEL_TMDL.exists():
        text = MODEL_TMDL.open(encoding="utf-8", newline="").read()
        eol = "\r\n" if "\r\n" in text else "\n"
        lines = text.split(eol)
        new_lines = [l for l in lines if "ref table 'SLA Threshold'" not in l and "ref table SLA Threshold" not in l]
        MODEL_TMDL.write_text(eol.join(new_lines), encoding="utf-8", newline="")
        print("  + Removed 'ref table SLA Threshold' from model.tmdl")
        
    if DIAGRAM_JSON.exists():
        try:
            ddata = json.loads(DIAGRAM_JSON.read_text(encoding="utf-8"))
            nodes = ddata.get("diagrams", [{}])[0].get("diagramNodes", [])
            ddata["diagrams"][0]["diagramNodes"] = [n for n in nodes if n.get("nodeIndex") != "SLA Threshold"]
            DIAGRAM_JSON.write_text(json.dumps(ddata, indent=2), encoding="utf-8")
            print("  + Cleaned diagramLayout.json")
        except Exception as e:
            print(f"  ! diagramLayout.json update skipped: {e}")

def delete_slicers_and_scratch_page():
    print("--- 2. Deleting SLA Threshold slicers & scratch page ---")
    for sd in SLICER_DIRS:
        if sd.exists():
            shutil.rmtree(sd)
            print(f"  + Deleted slicer visual: {sd.name}")
            
    if SCRATCH_PAGE4.exists():
        shutil.rmtree(SCRATCH_PAGE4)
        print("  + Deleted scratch Page 4 (50766f0da259202948c2)")
        
    if PAGES_JSON.exists():
        pdata = json.loads(PAGES_JSON.read_text(encoding="utf-8"))
        order = pdata.get("pageOrder", [])
        pdata["pageOrder"] = [pid for pid in order if pid != "50766f0da259202948c2"]
        PAGES_JSON.write_text(json.dumps(pdata, indent=2), encoding="utf-8")
        print("  + Removed Page 4 from pages.json pageOrder")

def update_executive_summary_visuals():
    print("--- 3. Restoring static headers on Executive Summary ---")
    # v06_kpi_openover30d
    v06_path = REPORT_PAGES / "47081098f92a957d7fd0" / "visuals" / "v06_kpi_openover30d" / "visual.json"
    if v06_path.exists():
        data = json.loads(v06_path.read_text(encoding="utf-8"))
        # Update projection to [Open Vulnerabilities >30 Days]
        data["visual"]["query"]["queryState"]["Data"]["projections"] = [
            {
                "field": {
                    "Measure": {
                        "Expression": {"SourceRef": {"Entity": "_Measures"}},
                        "Property": "Open Vulnerabilities >30 Days"
                    }
                },
                "queryRef": "_Measures.Open Vulnerabilities >30 Days",
                "nativeQueryRef": "Open Vulnerabilities > 30 Days"
            }
        ]
        # Update title to static text
        data["visual"]["visualContainerObjects"]["title"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Open Vulnerabilities > 30 Days'"}}},
                    "titleWrap": {"expr": {"Literal": {"Value": "true"}}}
                }
            }
        ]
        v06_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print("  + Updated v06_kpi_openover30d to static 'Open Vulnerabilities > 30 Days'")
        
    # v11_aging_barchart0
    v11_path = REPORT_PAGES / "47081098f92a957d7fd0" / "visuals" / "v11_aging_barchart0" / "visual.json"
    if v11_path.exists():
        data = json.loads(v11_path.read_text(encoding="utf-8"))
        data["visual"]["visualContainerObjects"]["title"] = [
            {
                "properties": {
                    "show": {"expr": {"Literal": {"Value": "true"}}},
                    "text": {"expr": {"Literal": {"Value": "'Open Vulnerabilities by Aging Bucket'"}}},
                    "titleWrap": {"expr": {"Literal": {"Value": "true"}}}
                }
            }
        ]
        v11_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print("  + Updated v11_aging_barchart0 to static 'Open Vulnerabilities by Aging Bucket'")

def update_measures():
    print("--- 4. Cleaning _Measures.tmdl from all SLA Threshold dependencies ---")
    text = MEASURES_TMDL.open(encoding="utf-8", newline="").read()
    eol = "\r\n" if "\r\n" in text else "\n"
    normalized = text.replace("\r\n", "\n")
    lines = normalized.split("\n")
    
    # Measures to completely delete
    measures_to_delete = {
        "Selected SLA Days",
        "Selected SLA Label",
        "Open Vulnerabilities Exceeding SLA"
    }
    
    # Measures to replace with clean, independent definitions
    replacement_measures = {
        "Open Vulnerabilities": """\tmeasure 'Open Vulnerabilities' =
\t\t\t// Total open Microsoft Windows findings
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open"
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 0ec3aee5-15e6-4ef3-b050-f1a008dd53ac""",

        "Open Vulnerabilities >30 Days": """\tmeasure 'Open Vulnerabilities >30 Days' =
\t\t\t// Metric 3: Open Microsoft Windows findings older than 30 days
\t\t\tVAR CutoffDate = TODAY() - 30
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Created Date] <= CutoffDate
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 36db6a06-451b-4cdf-8f2f-7251ec6337b2""",

        "Critical & High Vulnerabilities": """\tmeasure 'Critical & High Vulnerabilities' =
\t\t\t// Metric 1: Open Critical or High severity findings
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t\t('crowdstrike_vulnerability_device_reporting'[cve_severity] IN { "Critical", "High" }
\t\t\t\t\t|| 'crowdstrike_vulnerability_device_reporting'[cve_base_score] >= 7.0)
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 3cdbb094-7fd2-423c-875e-179715882585""",

        "CISA KEV Vulnerabilities": """\tmeasure 'CISA KEV Vulnerabilities' =
\t\t\t// Metric 2: Open CISA KEV findings
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[is_cisa_kev] = TRUE()
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 9ccf8ae5-c55e-4adc-a3f1-2ee0aa5d4cd7""",

        "Open Vulnerabilities by SLA Bucket": """\tmeasure 'Open Vulnerabilities by SLA Bucket' =
\t\t\t// Open vulnerabilities by aging bucket
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open"
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: bf0ffedc-8839-4954-91d4-53e05dfb2992""",

        "Closed Vulnerabilities by Closed Date": """\tmeasure 'Closed Vulnerabilities by Closed Date' =
\t\t\t// Closed findings activated via USERELATIONSHIP
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\tUSERELATIONSHIP('Calendar'[Date], 'crowdstrike_vulnerability_device_reporting'[Closed Date])
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 570cdc77-25a3-4147-9984-725ed7ccf8a7""",

        "Patching Rate %": """\tmeasure 'Patching Rate %' = ```
\t\t\t// Metric 5: Closed (Last 30 Days) / (Closed Last 30 Days + Open > 30 Days)
\t\t\tVAR CutoffDate = TODAY() - 30
\t\t\tVAR ClosedInPeriod = 
\t\t\t\tCALCULATE(
\t\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Closed Date] >= CutoffDate
\t\t\t\t)
\t\t\tVAR OpenOlderThan30 = [Open Vulnerabilities >30 Days]
\t\t\tVAR Workload = ClosedInPeriod + OpenOlderThan30
\t\t\tRETURN
\t\t\tDIVIDE(ClosedInPeriod, Workload, 0)
\t\t\t```
\t\tformatString: 0.0%
\t\tlineageTag: 01ba75a5-8541-44a5-a6d9-cbe774b6986f""",

        "Devices No Microsoft Remediation 30 Days": """\tmeasure 'Devices No Microsoft Remediation 30 Days' =
\t\t\tVAR CutoffDate = TODAY() - 30
\t\t\tRETURN
\t\t\tCOUNTROWS(
\t\t\t\tFILTER(
\t\t\t\t\tVALUES('crowdstrike_vulnerability_device_reporting'[aid]),
\t\t\t\t\tVAR LastMicrosoftClose =
\t\t\t\t\t\tCALCULATE(
\t\t\t\t\t\t\tMAX('crowdstrike_vulnerability_device_reporting'[Closed Date]),
\t\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t\t\t\tREMOVEFILTERS('Calendar')
\t\t\t\t\t\t)
\t\t\t\t\tRETURN
\t\t\t\t\t\tISBLANK(LastMicrosoftClose) || LastMicrosoftClose < CutoffDate
\t\t\t\t)
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: dad29aa2-617f-4a6e-a1fd-c0626ddebe79""",

        "Systems Not Rebooted in More Than 30 Days": """\tmeasure 'Systems Not Rebooted in More Than 30 Days' =
\t\t\tVAR CutoffDate = TODAY() - 30
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\tDISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[reporting_last_reboot] < CutoffDate
\t\t\t\t\t|| ISBLANK('crowdstrike_vulnerability_device_reporting'[reporting_last_reboot])
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: b53e1058-e8d0-49d8-9de7-1bb26ae4b2ea"""
    }

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if measure to delete
        deleted_match = None
        for dm in measures_to_delete:
            if line.startswith(f"\tmeasure '{dm}' ="):
                deleted_match = dm
                break
        if deleted_match:
            # Skip lines until next measure, column, or partition
            i += 1
            while i < len(lines) and not (lines[i].startswith("\tmeasure ") or lines[i].startswith("\tcolumn ") or lines[i].startswith("\tpartition ")):
                i += 1
            print(f"  + Deleted measure: {deleted_match}")
            continue

        # Check if measure to replace
        replaced_match = None
        for rm in replacement_measures:
            if line.startswith(f"\tmeasure '{rm}' ="):
                replaced_match = rm
                break
        if replaced_match:
            i += 1
            while i < len(lines) and not (lines[i].startswith("\tmeasure ") or lines[i].startswith("\tcolumn ") or lines[i].startswith("\tpartition ")):
                i += 1
            new_lines.append(replacement_measures[replaced_match])
            new_lines.append("")
            print(f"  + Restored clean definition for measure: {replaced_match}")
            continue

        new_lines.append(line)
        i += 1

    final_text = "\n".join(new_lines).replace("\n", "\r\n")
    MEASURES_TMDL.write_text(final_text, encoding="utf-8", newline="")
    print("  + _Measures.tmdl successfully updated and cleaned.")

def main():
    print("=== Permanently Removing SLA Threshold and All Dependencies ===")
    backup()
    delete_sla_table()
    delete_slicers_and_scratch_page()
    update_executive_summary_visuals()
    update_measures()
    print("=== Complete! ===")

if __name__ == "__main__":
    main()
