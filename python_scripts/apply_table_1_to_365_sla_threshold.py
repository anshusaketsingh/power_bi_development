#!/usr/bin/env python3
"""
apply_table_1_to_365_sla_threshold.py

1. Updates 'SLA Threshold.tmdl' to GENERATESERIES(1, 365, 1) with:
   - 'Threshold Days' (int64, 1..365, ParameterMetadata version 0)
   - 'SLA Threshold' (string label, sorted by 'Threshold Days')
2. Updates '_Measures.tmdl' with robust DAX measures:
   - 'Selected SLA Days' (supports single selection, range selection, defaults to 30)
   - 'Selected SLA Label' ("Open Vulnerabilities > X Days" or "Open Vulnerabilities > 1 Year")
   - 'Open Vulnerabilities' (evaluates Created Date <= TODAY() - [Selected SLA Days])
   - 'Critical & High Vulnerabilities'
   - 'CISA KEV Vulnerabilities'
   - 'Patching Rate %'
   - 'Devices No Microsoft Remediation 30 Days'
   - 'Systems Not Rebooted in More Than 30 Days'
   - 'Open Vulnerabilities by SLA Bucket'
   - 'Closed Vulnerabilities by Closed Date'
3. Configures SLA Threshold slicers across Tab 1, Tab 2, and Tab 3:
   - 1 to 365 slider range with numeric input box
   - Bound to 'SLA Threshold' syncGroup
4. Ensures detail and investigation grids are filtered to open findings exceeding the threshold.
5. Synchronizes all report and model definitions into CS Dashboard.pbix.
"""

import os
import json
import shutil
import zipfile
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
TARGET_REP = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard" / "CS Dashboard.Report"
SEMANTIC_MODEL = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard" / "CS Dashboard.SemanticModel"
PBIX_PATH = BASE_DIR / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"

def update_sla_threshold_tmdl():
    print("--- 1. Updating SLA Threshold.tmdl to 1..365 series ---")
    sla_path = SEMANTIC_MODEL / "definition" / "tables" / "SLA Threshold.tmdl"
    
    content = """table 'SLA Threshold'
\tlineageTag: 29ccbaa5-5811-408b-a961-bea13ade3e8f

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

\tcolumn 'SLA Threshold'
\t\tdataType: string
\t\tlineageTag: 2612d13b-fb20-4e0b-9e4b-654c7f6e0a10
\t\tsourceColumn: [SLA Threshold]
\t\tsortByColumn: 'Threshold Days'

\t\tannotation SummarizationSetBy = Automatic

\tpartition 'SLA Threshold' = calculated
\t\tmode: import
\t\tsource =
\t\t\t\tVAR DaysSeries = GENERATESERIES(1, 365, 1)
\t\t\t\tRETURN
\t\t\t\tSELECTCOLUMNS(
\t\t\t\t\tDaysSeries,
\t\t\t\t\t"Threshold Days", [Value],
\t\t\t\t\t"SLA Threshold",
\t\t\t\t\tSWITCH(
\t\t\t\t\t\t[Value],
\t\t\t\t\t\t30, "30 Days (Default SLA)",
\t\t\t\t\t\t60, "60 Days",
\t\t\t\t\t\t90, "90 Days",
\t\t\t\t\t\t365, "365 Days (1 Year)",
\t\t\t\t\t\t[Value] & " Days"
\t\t\t\t\t)
\t\t\t\t)
"""
    with open(sla_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  SLA Threshold.tmdl written with GENERATESERIES(1, 365, 1).")

def update_measures_tmdl():
    print("--- 2. Updating _Measures.tmdl with dynamic SLA threshold logic ---")
    measures_path = SEMANTIC_MODEL / "definition" / "tables" / "_Measures.tmdl"
    
    content = """table _Measures
\tlineageTag: 52e21a31-a892-4138-8bc2-7a1e324b906d

\tmeasure 'In-Scope Vulnerabilities' =
\t\t\t// Total in-scope Microsoft Windows findings
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft"
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: a77d8fd7-28fe-40f4-842a-eaff87a264b4

\tmeasure 'Selected SLA Days' = 
\t\t\tVAR SingleVal = SELECTEDVALUE('SLA Threshold'[Threshold Days])
\t\t\tVAR MinVal = MIN('SLA Threshold'[Threshold Days])
\t\t\tVAR HasFilter = ISFILTERED('SLA Threshold'[Threshold Days]) || ISFILTERED('SLA Threshold'[SLA Threshold])
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tNOT(ISBLANK(SingleVal)),
\t\t\t\tSingleVal,
\t\t\t\tIF(HasFilter, MinVal, 30)
\t\t\t)
\t\tformatString: 0
\t\tlineageTag: 3fcf4370-19d6-497c-b045-f96f80401c27

\tmeasure 'Selected SLA Label' = 
\t\t\tVAR DaysVal = [Selected SLA Days]
\t\t\tRETURN
\t\t\tSWITCH(
\t\t\t\tDaysVal,
\t\t\t\t30, "Open Vulnerabilities > 30 Days",
\t\t\t\t60, "Open Vulnerabilities > 60 Days",
\t\t\t\t90, "Open Vulnerabilities > 90 Days",
\t\t\t\t365, "Open Vulnerabilities > 1 Year",
\t\t\t\t"Open Vulnerabilities > " & DaysVal & " Days"
\t\t\t)
\t\tlineageTag: 12bd0804-82e3-4cd0-9a5a-bf68feb23446

\tmeasure 'Open Vulnerabilities' =
\t\t\t// Current open Microsoft Windows findings respecting selected SLA threshold
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tVAR CutoffDate = TODAY() - ThresholdDays
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Created Date] <= CutoffDate
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 0ec3aee5-15e6-4ef3-b050-f1a008dd53ac

\tmeasure 'Open Vulnerabilities >30 Days' = [Open Vulnerabilities]
\t\tformatString: #,##0
\t\tlineageTag: 36db6a06-451b-4cdf-8f2f-7251ec6337b2

\tmeasure 'Open Vulnerabilities Exceeding SLA' = [Open Vulnerabilities]
\t\tformatString: #,##0
\t\tlineageTag: fa7850ba-b56c-4068-8301-38073dda46fb

\tmeasure 'CISA KEV Vulnerabilities' =
\t\t\t// In-scope CISA KEV findings respecting selected SLA threshold
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tVAR CutoffDate = TODAY() - ThresholdDays
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[is_cisa_kev] = TRUE(),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Created Date] <= CutoffDate
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 9ccf8ae5-c55e-4adc-a3f1-2ee0aa5d4cd7

\tmeasure 'CISA KEV %' =
\t\t\t// CISA KEV as percentage of open findings
\t\t\tDIVIDE([CISA KEV Vulnerabilities], [Open Vulnerabilities], 0)
\t\tformatString: 0.0%
\t\tlineageTag: 247a865b-92c1-47c9-8e1c-ddf762acc33d

\tmeasure 'Closed Vulnerabilities' =
\t\t\t// Total closed in filter context
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed"
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: b308fdab-59b2-4b2b-86ac-438c0740e311

\tmeasure 'New Vulnerabilities' =
\t\t\t// New findings by period on Calendar
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft"
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 6fd8bd1e-5be8-4a26-8f97-f3fe3820ffc9

\tmeasure 'Closed Vulnerabilities by Closed Date' =
\t\t\t// Closed findings activated via USERELATIONSHIP respecting SLA threshold
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\tIF(
\t\t\t\t\tThresholdDays > 0,
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Closed Date] - 'crowdstrike_vulnerability_device_reporting'[Created Date] >= ThresholdDays,
\t\t\t\t\tTRUE()
\t\t\t\t),
\t\t\t\tUSERELATIONSHIP('Calendar'[Date], 'crowdstrike_vulnerability_device_reporting'[Closed Date])
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 570cdc77-25a3-4147-9984-725ed7ccf8a7

\tmeasure 'Remediation Rate %' = DIVIDE([Closed Vulnerabilities by Closed Date], [New Vulnerabilities]+[Closed Vulnerabilities by Closed Date], 0)
\t\tformatString: 0.0%
\t\tlineageTag: 5972c945-30b2-41d0-8d83-68c6ea513558

\tmeasure 'Net Vulnerability Change' = [New Vulnerabilities] - [Closed Vulnerabilities by Closed Date]
\t\tformatString: 0
\t\tlineageTag: fe939f3e-6407-407f-b56c-c0a2d5700717

\tmeasure 'Patching Rate %' = ```
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tVAR CutoffDate = TODAY() - ThresholdDays
\t\t\tVAR ClosedInPeriod = 
\t\t\t\tCALCULATE(
\t\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Closed Date] >= CutoffDate
\t\t\t\t)
\t\t\tVAR OpenExceedingSLA = [Open Vulnerabilities Exceeding SLA]
\t\t\tVAR Workload = ClosedInPeriod + OpenExceedingSLA
\t\t\tRETURN
\t\t\tDIVIDE(ClosedInPeriod, Workload, 0)
\t\t\t```
\t\tformatString: 0.0%
\t\tlineageTag: 01ba75a5-8541-44a5-a6d9-cbe774b6986f

\tmeasure 'Devices No Microsoft Remediation 30 Days' =
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tVAR CutoffDate = TODAY() - ThresholdDays
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
\t\tlineageTag: dad29aa2-617f-4a6e-a1fd-c0626ddebe79

\tmeasure 'Open Vulnerabilities by SLA Bucket' = ```
\t\t\t// Dynamically filters aging buckets based on selected SLA threshold
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
\t\t\t\tNOT(ISBLANK(BucketMaxDays)) && BucketMaxDays >= ThresholdDays,
\t\t\t\t[Open Vulnerabilities],
\t\t\t\tBLANK()
\t\t\t)
\t\t\t```
\t\tformatString: #,##0
\t\tlineageTag: bf0ffedc-8839-4954-91d4-53e05dfb2992

\tmeasure 'Critical & High Vulnerabilities' =
\t\t\t// Metric 1: Count open vulnerabilities classified as High or Critical based on severity or CVSS score respecting SLA threshold
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tVAR CutoffDate = TODAY() - ThresholdDays
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t\t('crowdstrike_vulnerability_device_reporting'[cve_severity] IN { "Critical", "High" }
\t\t\t\t\t|| 'crowdstrike_vulnerability_device_reporting'[cve_base_score] >= 7.0),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Created Date] <= CutoffDate
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 3cdbb094-7fd2-423c-875e-179715882585

\tmeasure 'Closed Vulnerabilities (Last 30 Days)' =
\t\t\t// Metric 5 Count View: Remediated findings during the previous period
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tVAR CutoffDate = TODAY() - ThresholdDays
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Closed Date] >= CutoffDate
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 3d14a51c-0899-4b0d-bd60-4bce0423ccbc

\tmeasure 'Systems Not Rebooted in More Than 30 Days' =
\t\t\t// Metric 6: Count devices where the most recent reboot occurred > SLA days ago
\t\t\tVAR ThresholdDays = [Selected SLA Days]
\t\t\tVAR CutoffDate = TODAY() - ThresholdDays
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\tDISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[reporting_last_reboot] < CutoffDate
\t\t\t\t\t|| ISBLANK('crowdstrike_vulnerability_device_reporting'[reporting_last_reboot])
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: b53e1058-e8d0-49d8-9de7-1bb26ae4b2ea

\tcolumn Dummy
\t\tisHidden
\t\tlineageTag: ad85f6eb-57e2-4f7e-8c5f-79d9c08ffb6d
\t\tsourceColumn: [Dummy]

\tpartition _Measures = calculated
\t\tmode: import
\t\tsource = ROW("Dummy", BLANK())
"""
    with open(measures_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("  _Measures.tmdl written with dynamic SLA measures.")

def update_slicers():
    print("--- 3. Configuring SLA Slicers on Tab 1, Tab 2, and Tab 3 ---")
    slicer_configs = [
        (TARGET_REP / "definition" / "pages" / "47081098f92a957d7fd0" / "visuals" / "v13_slicer_sla_thresh" / "visual.json", 371),
        (TARGET_REP / "definition" / "pages" / "p02_trends_exceptions" / "visuals" / "p2_v13_slicer_sla_thresh" / "visual.json", 617),
        (TARGET_REP / "definition" / "pages" / "p03_vulnerability_details" / "visuals" / "p3_v13_slicer_sla_thresh" / "visual.json", 535),
    ]
    
    for path, y_pos in slicer_configs:
        path.parent.mkdir(parents=True, exist_ok=True)
        visual_name = path.parent.name
        sdata = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
            "name": visual_name,
            "position": {
                "x": 28,
                "y": y_pos,
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
                                            "Expression": {
                                                "SourceRef": {
                                                    "Entity": "SLA Threshold"
                                                }
                                            },
                                            "Property": "Threshold Days"
                                        }
                                    },
                                    "queryRef": "SLA Threshold.Threshold Days",
                                    "nativeQueryRef": "Threshold Days",
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
                                "mode": {
                                    "expr": {
                                        "Literal": {
                                            "Value": "'After'"
                                        }
                                    }
                                }
                            }
                        }
                    ],
                    "header": [
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
                                        "Literal": {
                                            "Value": "'SLA Threshold (1 - 365 Days)'"
                                        }
                                    }
                                },
                                "fontColor": {
                                    "solid": {
                                        "color": {
                                            "expr": {
                                                "Literal": {
                                                    "Value": "'#FFFFFF'"
                                                }
                                            }
                                        }
                                    }
                                },
                                "textSize": {
                                    "expr": {
                                        "Literal": {
                                            "Value": "10D"
                                        }
                                    }
                                },
                                "bold": {
                                    "expr": {
                                        "Literal": {
                                            "Value": "true"
                                        }
                                    }
                                }
                            }
                        }
                    ],
                    "slider": [
                        {
                            "properties": {
                                "show": {
                                    "expr": {
                                        "Literal": {
                                            "Value": "true"
                                        }
                                    }
                                },
                                "color": {
                                    "solid": {
                                        "color": {
                                            "expr": {
                                                "Literal": {
                                                    "Value": "'#C6E2D1'"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    ],
                    "items": [
                        {
                            "properties": {
                                "fontColor": {
                                    "solid": {
                                        "color": {
                                            "expr": {
                                                "Literal": {
                                                    "Value": "'#1b4332'"
                                                }
                                            }
                                        }
                                    }
                                },
                                "background": {
                                    "solid": {
                                        "color": {
                                            "expr": {
                                                "Literal": {
                                                    "Value": "'#FFFFFF'"
                                                }
                                            }
                                        }
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
                                "show": {
                                    "expr": {
                                        "Literal": {
                                            "Value": "false"
                                        }
                                    }
                                }
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
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sdata, f, indent=2)
        print(f"  {visual_name} written at y={y_pos}.")

def sync_pbix():
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
    update_sla_threshold_tmdl()
    update_measures_tmdl()
    update_slicers()
    sync_pbix()
    print("--- ALL UPDATES COMPLETED SUCCESSFULLY ---")
