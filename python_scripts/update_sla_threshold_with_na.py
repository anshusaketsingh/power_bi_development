"""
update_sla_threshold_with_na.py

1. Updates 'SLA Threshold.tmdl' to include 'N/A' (Threshold Days = 0) followed by 1 to 365 Days,
   with strict sort ordering so 'N/A' is always first.
2. Updates measures in '_Measures.tmdl':
   - [Selected SLA Days]: Returns BLANK() when N/A is selected or when no filter is applied.
   - [Selected SLA Label]: Returns "Open Vulnerabilities (All / SLA N/A)" when N/A is selected.
   - [Open Vulnerabilities]: Returns all open findings when N/A (no age cutoff applied).
   - [Critical & High Vulnerabilities]: Returns all open Crit/High findings when N/A.
   - [CISA KEV Vulnerabilities]: Returns all open CISA KEV findings when N/A.
   - [Open Vulnerabilities by SLA Bucket]: Shows all aging buckets when N/A.
   - [Closed Vulnerabilities by Closed Date]: Shows all closed findings when N/A.
   - [Patching Rate %]: Calculates overall closed / total open+closed when N/A.
3. Updates the 4 synced SLA Threshold slicers across all pages:
   - Projects 'SLA Threshold' (string column with 'N/A', '1 Day', '2 Days', etc.)
   - Pre-selects 'N/A' by default
   - Allows users to pick any number between 1 and 365 days, and seamlessly switch back to N/A.
"""

import json
import shutil
import time
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
SEMANTIC_MODEL = PROJ / "CS Dashboard.SemanticModel" / "definition" / "tables"
SLA_TMDL = SEMANTIC_MODEL / "SLA Threshold.tmdl"
MEASURES_TMDL = SEMANTIC_MODEL / "_Measures.tmdl"
REPORT_PAGES = PROJ / "CS Dashboard.Report" / "definition" / "pages"

VISUAL_PATHS = [
    REPORT_PAGES / "47081098f92a957d7fd0" / "visuals" / "v13_slicer_sla_thresh" / "visual.json",
    REPORT_PAGES / "p02_trends_exceptions" / "visuals" / "p2_v13_slicer_sla_thresh" / "visual.json",
    REPORT_PAGES / "p03_vulnerability_details" / "visuals" / "p3_v13_slicer_sla_thresh" / "visual.json",
    REPORT_PAGES / "p05_vulnerability_details" / "visuals" / "p5_v13_slicer_sla_thresh" / "visual.json"
]

VISUAL_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"
DARK_GREEN = "#1b4332"

def backup():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BASE_DIR / "development" / "jh_crowd_strike" / "backups" / f"pre_sla_na_update_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    if SLA_TMDL.exists():
        shutil.copy2(SLA_TMDL, dest / "SLA Threshold.tmdl")
    if MEASURES_TMDL.exists():
        shutil.copy2(MEASURES_TMDL, dest / "_Measures.tmdl")
    for vp in VISUAL_PATHS:
        if vp.exists():
            (dest / vp.parent.name).mkdir(parents=True, exist_ok=True)
            shutil.copy2(vp, dest / vp.parent.name / "visual.json")
    print(f"Pre-flight backup saved at: {dest}")

def update_sla_threshold_table():
    print("--- 1. Updating SLA Threshold.tmdl with 'N/A' option ---")
    content = """table 'SLA Threshold'
\tlineageTag: 29ccbaa5-5811-408b-a961-bea13ade3e8f

\tcolumn 'SLA Threshold'
\t\tdataType: string
\t\tlineageTag: 2612d13b-fb20-4e0b-9e4b-654c7f6e0a10
\t\tsourceColumn: [SLA Threshold]
\t\tsortByColumn: 'Threshold Days'

\t\tannotation SummarizationSetBy = Automatic

\tcolumn 'Threshold Days'
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: dd153c8a-1442-4abd-a444-1a2d68c2f7bf
\t\tsummarizeBy: none
\t\tsourceColumn: [Threshold Days]

\t\textendedProperty ParameterMetadata =
\t\t\t\t{
\t\t\t\t  "version": 0
\t\t\t\t}

\t\tannotation SummarizationSetBy = User

\tpartition 'SLA Threshold' = calculated
\t\tmode: import
\t\tsource =
\t\t\t\tVAR DaysSeries = GENERATESERIES(1, 365, 1)
\t\t\t\tVAR LabeledSeries =
\t\t\t\t\tSELECTCOLUMNS(
\t\t\t\t\t\tDaysSeries,
\t\t\t\t\t\t"Threshold Days", [Value],
\t\t\t\t\t\t"SLA Threshold",
\t\t\t\t\t\tSWITCH(
\t\t\t\t\t\t\t[Value],
\t\t\t\t\t\t\t1, "1 Day",
\t\t\t\t\t\t\t30, "30 Days (Default SLA)",
\t\t\t\t\t\t\t60, "60 Days",
\t\t\t\t\t\t\t90, "90 Days",
\t\t\t\t\t\t\t365, "365 Days (1 Year)",
\t\t\t\t\t\t\t[Value] & " Days"
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\tVAR NaRow =
\t\t\t\t\tROW(
\t\t\t\t\t\t"Threshold Days", 0,
\t\t\t\t\t\t"SLA Threshold", "N/A"
\t\t\t\t\t)
\t\t\t\tRETURN
\t\t\t\tUNION(NaRow, LabeledSeries)

"""
    content_crlf = content.replace("\r\n", "\n").replace("\n", "\r\n")
    SLA_TMDL.write_text(content_crlf, encoding="utf-8", newline="")
    print("  + SLA Threshold.tmdl updated with 'N/A' (Day 0) and 1..365 Days.")

def update_measures():
    print("--- 2. Updating _Measures.tmdl for N/A SLA support ---")
    text = MEASURES_TMDL.open(encoding="utf-8", newline="").read()
    
    # Measure definitions
    updated_measures = {
        "Selected SLA Days": """\tmeasure 'Selected SLA Days' =
\t\t\tVAR SelectedDay = SELECTEDVALUE('SLA Threshold'[Threshold Days])
\t\t\tVAR SelectedLabel = SELECTEDVALUE('SLA Threshold'[SLA Threshold])
\t\t\tVAR HasFilter = ISFILTERED('SLA Threshold'[Threshold Days]) || ISFILTERED('SLA Threshold'[SLA Threshold])
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tNOT(HasFilter) || SelectedLabel = "N/A" || SelectedDay = 0,
\t\t\t\tBLANK(),
\t\t\t\tIF(NOT(ISBLANK(SelectedDay)), SelectedDay, BLANK())
\t\t\t)
\t\tformatString: 0
\t\tlineageTag: 3fcf4370-19d6-497c-b045-f96f80401c27""",

        "Selected SLA Label": """\tmeasure 'Selected SLA Label' =
\t\t\tVAR DaysVal = [Selected SLA Days]
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tISBLANK(DaysVal) || DaysVal <= 0,
\t\t\t\t"Open Vulnerabilities (All / SLA N/A)",
\t\t\t\tSWITCH(
\t\t\t\t\tDaysVal,
\t\t\t\t\t30, "Open Vulnerabilities > 30 Days",
\t\t\t\t\t60, "Open Vulnerabilities > 60 Days",
\t\t\t\t\t90, "Open Vulnerabilities > 90 Days",
\t\t\t\t\t365, "Open Vulnerabilities > 1 Year",
\t\t\t\t\t"Open Vulnerabilities > " & DaysVal & " Days"
\t\t\t\t)
\t\t\t)
\t\tlineageTag: 12bd0804-82e3-4cd0-9a5a-bf68feb23446""",

        "Open Vulnerabilities": """\tmeasure 'Open Vulnerabilities' =
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tISBLANK(ThresholdDays) || ThresholdDays <= 0,
\t\t\t\tCALCULATE(
\t\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open"
\t\t\t\t),
\t\t\t\tVAR CutoffDate = TODAY() - ThresholdDays
\t\t\t\tRETURN
\t\t\t\tCALCULATE(
\t\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Created Date] <= CutoffDate
\t\t\t\t)
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 0ec3aee5-15e6-4ef3-b050-f1a008dd53ac""",

        "Critical & High Vulnerabilities": """\tmeasure 'Critical & High Vulnerabilities' =
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tISBLANK(ThresholdDays) || ThresholdDays <= 0,
\t\t\t\tCALCULATE(
\t\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t\t\t('crowdstrike_vulnerability_device_reporting'[cve_severity] IN { "Critical", "High" }
\t\t\t\t\t\t|| 'crowdstrike_vulnerability_device_reporting'[cve_base_score] >= 7.0)
\t\t\t\t),
\t\t\t\tVAR CutoffDate = TODAY() - ThresholdDays
\t\t\t\tRETURN
\t\t\t\tCALCULATE(
\t\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t\t\t('crowdstrike_vulnerability_device_reporting'[cve_severity] IN { "Critical", "High" }
\t\t\t\t\t\t|| 'crowdstrike_vulnerability_device_reporting'[cve_base_score] >= 7.0),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Created Date] <= CutoffDate
\t\t\t\t)
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 3cdbb094-7fd2-423c-875e-179715882585""",

        "CISA KEV Vulnerabilities": """\tmeasure 'CISA KEV Vulnerabilities' =
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tISBLANK(ThresholdDays) || ThresholdDays <= 0,
\t\t\t\tCALCULATE(
\t\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[is_cisa_kev] = TRUE()
\t\t\t\t),
\t\t\t\tVAR CutoffDate = TODAY() - ThresholdDays
\t\t\t\tRETURN
\t\t\t\tCALCULATE(
\t\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[is_cisa_kev] = TRUE(),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Created Date] <= CutoffDate
\t\t\t\t)
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 9ccf8ae5-c55e-4adc-a3f1-2ee0aa5d4cd7""",

        "Open Vulnerabilities by SLA Bucket": """\tmeasure 'Open Vulnerabilities by SLA Bucket' = ```
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tVAR CurrentBucket = SELECTEDVALUE('crowdstrike_vulnerability_device_reporting'[Age Bucket])
\t\t\tVAR BucketMaxDays = 
\t\t\t\tSWITCH(
\t\t\t\t\tCurrentBucket,
\t\t\t\t\t"0-30 Days", 30,
\t\t\t\t\t"31-60 Days", 60,
\t\t\t\t\t"61-90 Days", 90,
\t\t\t\t\t"91-365 Days", 365,
\t\t\t\t\t">1 Year", 99999,
\t\t\t\t\tBLANK()
\t\t\t\t)
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tISBLANK(ThresholdDays) || ThresholdDays <= 0,
\t\t\t\t[Open Vulnerabilities],
\t\t\t\tIF(
\t\t\t\t\tNOT(ISBLANK(BucketMaxDays)) && BucketMaxDays >= ThresholdDays,
\t\t\t\t\t[Open Vulnerabilities],
\t\t\t\t\tBLANK()
\t\t\t\t)
\t\t\t)
\t\t\t```
\t\tformatString: #,##0
\t\tlineageTag: bf0ffedc-8839-4954-91d4-53e05dfb2992""",

        "Closed Vulnerabilities by Closed Date": """\tmeasure 'Closed Vulnerabilities by Closed Date' =
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tISBLANK(ThresholdDays) || ThresholdDays <= 0,
\t\t\t\tCALCULATE(
\t\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t\tUSERELATIONSHIP('Calendar'[Date], 'crowdstrike_vulnerability_device_reporting'[Closed Date])
\t\t\t\t),
\t\t\t\tCALCULATE(
\t\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Closed Date] - 'crowdstrike_vulnerability_device_reporting'[Created Date] >= ThresholdDays,
\t\t\t\t\tUSERELATIONSHIP('Calendar'[Date], 'crowdstrike_vulnerability_device_reporting'[Closed Date])
\t\t\t\t)
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 570cdc77-25a3-4147-9984-725ed7ccf8a7""",

        "Patching Rate %": """\tmeasure 'Patching Rate %' = ```
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tISBLANK(ThresholdDays) || ThresholdDays <= 0,
\t\t\t\tVAR TotalClosed = [Closed Vulnerabilities]
\t\t\t\tVAR TotalOpen = [Open Vulnerabilities]
\t\t\t\tRETURN DIVIDE(TotalClosed, TotalClosed + TotalOpen, 0),
\t\t\t\tVAR CutoffDate = TODAY() - ThresholdDays
\t\t\t\tVAR ClosedInPeriod = 
\t\t\t\t\tCALCULATE(
\t\t\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Closed Date] >= CutoffDate
\t\t\t\t\t)
\t\t\t\tVAR OpenExceedingSLA = [Open Vulnerabilities Exceeding SLA]
\t\t\t\tVAR Workload = ClosedInPeriod + OpenExceedingSLA
\t\t\t\tRETURN
\t\t\t\tDIVIDE(ClosedInPeriod, Workload, 0)
\t\t\t)
\t\t\t```
\t\tformatString: 0.0%
\t\tlineageTag: 01ba75a5-8541-44a5-a6d9-cbe774b6986f"""
    }

    # Replace each measure definition
    # Normalize text to LF for regex/split, then restore CRLF
    normalized = text.replace("\r\n", "\n")
    
    # We will parse by measure blocks
    lines = normalized.split("\n")
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        matched_m = None
        for m_name in updated_measures:
            if line.startswith(f"\tmeasure '{m_name}' ="):
                matched_m = m_name
                break
        
        if matched_m:
            # Skip until next measure or column or end
            i += 1
            while i < len(lines) and not (lines[i].startswith("\tmeasure ") or lines[i].startswith("\tcolumn ") or lines[i].startswith("\tpartition ")):
                i += 1
            # Insert new definition
            new_lines.append(updated_measures[matched_m])
            new_lines.append("")
        else:
            new_lines.append(line)
            i += 1

    final_text = "\n".join(new_lines).replace("\n", "\r\n")
    MEASURES_TMDL.write_text(final_text, encoding="utf-8", newline="")
    print("  + _Measures.tmdl updated with all dynamic N/A measures.")

def update_slicers():
    print("--- 3. Updating SLA Threshold Slicers across all pages ---")
    
    for vp in VISUAL_PATHS:
        if not vp.exists():
            print(f"  ! Slicer file missing, skipped: {vp}")
            continue
            
        v_name = vp.parent.name
        data = {
            "$schema": VISUAL_SCHEMA,
            "name": v_name,
            "position": {
                "x": 28,
                "y": 617 if ("p05" in str(vp) or "p02" in str(vp)) else (535 if "p03" in str(vp) else 371),
                "z": 12000,
                "height": 72,
                "width": 275,
                "tabOrder": 12000
            },
            "visual": {
                "visualType": "slicer",
                "query": {
                    "queryState": {
                        "Values": {
                            "projections": [
                                {
                                    "field": {
                                        "Column": {
                                            "Expression": {"SourceRef": {"Entity": "SLA Threshold"}},
                                            "Property": "SLA Threshold"
                                        }
                                    },
                                    "queryRef": "SLA Threshold.SLA Threshold",
                                    "nativeQueryRef": "SLA Threshold",
                                    "active": True
                                }
                            ]
                        }
                    }
                },
                "objects": {
                    "data": [
                        {
                            "properties": {
                                "mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}},
                                "isInvertedSelectionMode": {"expr": {"Literal": {"Value": "true"}}}
                            }
                        }
                    ],
                    "header": [
                        {
                            "properties": {
                                "show": {"expr": {"Literal": {"Value": "true"}}},
                                "text": {"expr": {"Literal": {"Value": "'SLA Threshold'"}}},
                                "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}},
                                "textSize": {"expr": {"Literal": {"Value": "10D"}}},
                                "bold": {"expr": {"Literal": {"Value": "true"}}}
                            }
                        }
                    ],
                    "items": [
                        {
                            "properties": {
                                "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1b4332'"}}}}},
                                "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}
                            }
                        }
                    ],
                    "selection": [
                        {
                            "properties": {
                                "selectAllCheckboxEnabled": {"expr": {"Literal": {"Value": "true"}}}
                            }
                        }
                    ],
                    "general": [
                        {
                            "properties": {
                                "filter": {
                                    "filter": {
                                        "Version": 2,
                                        "From": [
                                            {
                                                "Name": "s",
                                                "Entity": "SLA Threshold",
                                                "Type": 0
                                            }
                                        ],
                                        "Where": [
                                            {
                                                "Condition": {
                                                    "In": {
                                                        "Expressions": [
                                                            {
                                                                "Column": {
                                                                    "Expression": {
                                                                        "SourceRef": {
                                                                            "Source": "s"
                                                                        }
                                                                    },
                                                                    "Property": "SLA Threshold"
                                                                }
                                                            }
                                                        ],
                                                        "Values": [
                                                            [
                                                                {
                                                                    "Literal": {
                                                                        "Value": "'N/A'"
                                                                    }
                                                                }
                                                            ]
                                                        ]
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    ]
                },
                "visualContainerObjects": {
                    "background": [
                        {
                            "properties": {
                                "show": {"expr": {"Literal": {"Value": "false"}}}
                            }
                        }
                    ]
                },
                "syncGroup": {
                    "groupName": "SLA Threshold",
                    "fieldChanges": True,
                    "filterChanges": True
                }
            }
        }
        
        vp.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"  + Updated {vp.parent.name} to project 'SLA Threshold' with 'N/A' pre-selected.")

def main():
    print("=== Implementing SLA Threshold 'N/A' Option by Default ===")
    backup()
    update_sla_threshold_table()
    update_measures()
    update_slicers()
    print("=== Complete! ===")

if __name__ == "__main__":
    main()
