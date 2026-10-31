"""
build_cs_dashboard.py
Reusable Power BI Dashboard and PBIP Builder for CrowdStrike Windows Vulnerability & Patch Compliance.
Conforms to Microsoft Skills for Fabric PBIP and PBIR standards.
"""

import os
import json
import zipfile
import shutil
from pathlib import Path
from dotenv import load_dotenv

# Load configuration from .env
load_dotenv()

WORKSPACE_ROOT = Path(os.getenv("WORKSPACE_ROOT", "."))
PBIX_PATH = WORKSPACE_ROOT / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"
PBIP_TARGET_DIR = WORKSPACE_ROOT / "development" / "jh_crowd_strike" / "CS_Dashboard"

def generate_tmdl_definitions(out_dir: Path):
    """Generates TMDL semantic model definitions."""
    sem_dir = out_dir / "CS_Dashboard.SemanticModel"
    def_dir = sem_dir / "definition"
    tables_dir = def_dir / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)

    # 1. definition.pbism
    pbism = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
        "version": "4.2",
        "settings": {
            "qnaEnabled": True
        }
    }
    with open(sem_dir / "definition.pbism", "w", encoding="utf-8") as f:
        json.dump(pbism, f, indent=2)

    # 2. database.tmdl
    with open(def_dir / "database.tmdl", "w", encoding="utf-8") as f:
        f.write("database 7124f8d8-6199-44fe-b35d-7f7f06b3e1c6\n")
        f.write("\tcompatibilityLevel: 1702\n")
        f.write("\tcompatibilityMode: powerBI\n")
        f.write("\tlanguage: 1033\n")

    # 3. model.tmdl
    with open(def_dir / "model.tmdl", "w", encoding="utf-8") as f:
        f.write("model Model\n")
        f.write("\tculture: en-US\n")
        f.write("\tdefaultPowerBIDataSourceVersion: powerBI_V3\n")
        f.write("\tsourceQueryCulture: en-US\n\n")
        f.write("ref table _Measures\n")
        f.write("ref table Calendar\n")
        f.write("ref table Vulnerabilities\n")

    # 4. relationships.tmdl
    with open(def_dir / "relationships.tmdl", "w", encoding="utf-8") as f:
        f.write("relationship 'Calendar to Vulnerabilities Created Date'\n")
        f.write("\tfromColumn: Vulnerabilities.'Created Date'\n")
        f.write("\ttoColumn: Calendar.Date\n\n")
        f.write("relationship 'Calendar to Vulnerabilities Closed Date'\n")
        f.write("\tisActive: false\n")
        f.write("\tfromColumn: Vulnerabilities.'Closed Date'\n")
        f.write("\ttoColumn: Calendar.Date\n")

    # 5. tables/_Measures.tmdl
    measures_tmdl = """table _Measures

\tmeasure 'In-Scope Vulnerabilities' = ```
\t\t// Total in-scope Microsoft Windows findings
\t\tCALCULATE(
\t\t\tCOUNTROWS('Vulnerabilities'),
\t\t\t'Vulnerabilities'[Platform] = "Windows",
\t\t\t'Vulnerabilities'[Vendor Normalized] = "Microsoft"
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'Open Vulnerabilities' = ```
\t\t// Current open Microsoft Windows findings
\t\tCALCULATE(
\t\t\tCOUNTROWS('Vulnerabilities'),
\t\t\t'Vulnerabilities'[Platform] = "Windows",
\t\t\t'Vulnerabilities'[Vendor Normalized] = "Microsoft",
\t\t\t'Vulnerabilities'[Status] = "Open"
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'Open Vulnerabilities >30 Days' = ```
\t\t// Open Microsoft Windows findings older than 30 days SLA
\t\tVAR CutoffDate = TODAY() - 30
\t\tRETURN
\t\tCALCULATE(
\t\t\tCOUNTROWS('Vulnerabilities'),
\t\t\t'Vulnerabilities'[Platform] = "Windows",
\t\t\t'Vulnerabilities'[Vendor Normalized] = "Microsoft",
\t\t\t'Vulnerabilities'[Status] = "Open",
\t\t\t'Vulnerabilities'[Created Date] <= CutoffDate
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'CISA KEV Vulnerabilities' = ```
\t\t// In-scope findings marked as CISA Known Exploited Vulnerability
\t\tCALCULATE(
\t\t\tCOUNTROWS('Vulnerabilities'),
\t\t\t'Vulnerabilities'[Platform] = "Windows",
\t\t\t'Vulnerabilities'[Vendor Normalized] = "Microsoft",
\t\t\t'Vulnerabilities'[Status] = "Open",
\t\t\t'Vulnerabilities'[is_cisa_kev] = TRUE()
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'CISA KEV %' = ```
\t\t// CISA KEV as percentage of open vulnerabilities
\t\tDIVIDE([CISA KEV Vulnerabilities], [Open Vulnerabilities], 0)
\t\t```
\t\tformatString: 0.0%

\tmeasure 'Closed Vulnerabilities' = ```
\t\t// Total closed findings in current filter context
\t\tCALCULATE(
\t\t\tCOUNTROWS('Vulnerabilities'),
\t\t\t'Vulnerabilities'[Platform] = "Windows",
\t\t\t'Vulnerabilities'[Vendor Normalized] = "Microsoft",
\t\t\t'Vulnerabilities'[Status] = "Closed"
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'New Vulnerabilities' = ```
\t\t// Counts new findings by period on Calendar
\t\tCALCULATE(
\t\t\tCOUNTROWS('Vulnerabilities'),
\t\t\t'Vulnerabilities'[Platform] = "Windows",
\t\t\t'Vulnerabilities'[Vendor Normalized] = "Microsoft"
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'Closed Vulnerabilities by Closed Date' = ```
\t\t// Uses inactive Calendar relationship to trend remediation by closed date
\t\tCALCULATE(
\t\t\tCOUNTROWS('Vulnerabilities'),
\t\t\t'Vulnerabilities'[Platform] = "Windows",
\t\t\t'Vulnerabilities'[Vendor Normalized] = "Microsoft",
\t\t\t'Vulnerabilities'[Status] = "Closed",
\t\t\tUSERELATIONSHIP('Calendar'[Date], 'Vulnerabilities'[Closed Date])
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'Remediation Rate %' = ```
\t\t// Remediation Rate %
\t\tDIVIDE([Closed Vulnerabilities by Closed Date], [New Vulnerabilities], 0)
\t\t```
\t\tformatString: 0.0%

\tmeasure 'Net Vulnerability Change' = ```
\t\t// Net intake vs closed change for period
\t\t[New Vulnerabilities] - [Closed Vulnerabilities by Closed Date]
\t\t```
\t\tformatString: +#,-#;0

\tmeasure 'Patching Rate %' = ```
\t\t// 30-Day Patching Compliance Rate %
\t\tVAR Closed30 = 
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('Vulnerabilities'),
\t\t\t\t'Vulnerabilities'[Platform] = "Windows",
\t\t\t\t'Vulnerabilities'[Vendor Normalized] = "Microsoft",
\t\t\t\t'Vulnerabilities'[Status] = "Closed",
\t\t\t\t'Vulnerabilities'[Closed Date] >= (TODAY() - 30)
\t\t\t)
\t\tVAR OpenOver30 = [Open Vulnerabilities >30 Days]
\t\tVAR Workload = Closed30 + OpenOver30
\t\tRETURN
\t\tDIVIDE(Closed30, Workload, 0)
\t\t```
\t\tformatString: 0.0%

\tmeasure 'Devices No Microsoft Remediation 30 Days' = ```
\t\t// Unique devices with no Microsoft closures in previous 30 days
\t\tVAR CutoffDate = TODAY() - 30
\t\tRETURN
\t\tCOUNTROWS(
\t\t\tFILTER(
\t\t\t\tVALUES('Vulnerabilities'[Device ID]),
\t\t\t\tVAR LastMicrosoftClose =
\t\t\t\t\tCALCULATE(
\t\t\t\t\t\tMAX('Vulnerabilities'[Closed Date]),
\t\t\t\t\t\t'Vulnerabilities'[Platform] = "Windows",
\t\t\t\t\t\t'Vulnerabilities'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t\t'Vulnerabilities'[Status] = "Closed",
\t\t\t\t\t\tREMOVEFILTERS('Calendar')
\t\t\t\t\t)
\t\t\t\tRETURN
\t\t\t\t\tISBLANK(LastMicrosoftClose) || LastMicrosoftClose < CutoffDate
\t\t\t)
\t\t)
\t\t```
\t\tformatString: #,##0

\tcolumn Dummy
\t\tisHidden
\t\tsourceColumn: [Dummy]

\tpartition _Measures = calculated
\t\tmode: import
\t\tsource = ROW("Dummy", BLANK())
"""
    with open(tables_dir / "_Measures.tmdl", "w", encoding="utf-8") as f:
        f.write(measures_tmdl)

    # 6. tables/Calendar.tmdl
    calendar_tmdl = """table Calendar
\tdataCategory: Time

\tcolumn Date
\t\tdataType: dateTime
\t\tisKey
\t\tformatString: yyyy-mm-dd
\t\tsourceColumn: [Date]

\tcolumn Year
\t\tdataType: int64
\t\tsummarizeBy: none
\t\tsourceColumn: [Year]

\tcolumn 'Year Quarter'
\t\tdataType: string
\t\tsourceColumn: [Year Quarter]

\tcolumn Quarter
\t\tdataType: string
\t\tsourceColumn: [Quarter]

\tcolumn 'Quarter Number'
\t\tdataType: int64
\t\tisHidden
\t\tsummarizeBy: none
\t\tsourceColumn: [Quarter Number]

\tcolumn 'Year Month'
\t\tdataType: string
\t\tsourceColumn: [Year Month]

\tcolumn 'Month Name'
\t\tdataType: string
\t\tsortByColumn: 'Month Number'
\t\tsourceColumn: [Month Name]

\tcolumn 'Month Short'
\t\tdataType: string
\t\tsortByColumn: 'Month Number'
\t\tsourceColumn: [Month Short]

\tcolumn 'Month Number'
\t\tdataType: int64
\t\tisHidden
\t\tsummarizeBy: none
\t\tsourceColumn: [Month Number]

\tcolumn 'Week Start'
\t\tdataType: dateTime
\t\tformatString: yyyy-mm-dd
\t\tsourceColumn: [Week Start]

\tcolumn 'Week End'
\t\tdataType: dateTime
\t\tformatString: yyyy-mm-dd
\t\tsourceColumn: [Week End]

\tcolumn 'Week Number'
\t\tdataType: int64
\t\tsummarizeBy: none
\t\tsourceColumn: [Week Number]

\tcolumn 'Year Week'
\t\tdataType: string
\t\tsortByColumn: 'Week Start'
\t\tsourceColumn: [Year Week]

\tcolumn 'Day of Week'
\t\tdataType: string
\t\tsortByColumn: 'Day Number of Week'
\t\tsourceColumn: [Day of Week]

\tcolumn 'Day of Week Short'
\t\tdataType: string
\t\tsortByColumn: 'Day Number of Week'
\t\tsourceColumn: [Day of Week Short]

\tcolumn 'Day Number of Week'
\t\tdataType: int64
\t\tisHidden
\t\tsummarizeBy: none
\t\tsourceColumn: [Day Number of Week]

\tcolumn 'Is Past'
\t\tdataType: boolean
\t\tsourceColumn: [Is Past]

\tcolumn 'Is Current Week'
\t\tdataType: boolean
\t\tsourceColumn: [Is Current Week]

\tcolumn 'Relative Day Offset'
\t\tdataType: int64
\t\tsummarizeBy: none
\t\tsourceColumn: [Relative Day Offset]

\tcolumn 'Relative Week Offset'
\t\tdataType: int64
\t\tsummarizeBy: none
\t\tsourceColumn: [Relative Week Offset]

\tpartition Calendar = calculated
\t\tmode: import
\t\tsource = ```
\t\t\tVAR MinFactDate = MIN('Vulnerabilities'[Created Date])
\t\t\tVAR MaxFactDate = MAXX(
\t\t\t\t'Vulnerabilities',
\t\t\t\tCOALESCE('Vulnerabilities'[Closed Date], 'Vulnerabilities'[Created Date])
\t\t\t)
\t\t\tVAR StartDate = DATE(YEAR(COALESCE(MinFactDate, TODAY() - 365)), 1, 1)
\t\t\tVAR EndDate = DATE(YEAR(COALESCE(MaxFactDate, TODAY())), 12, 31)
\t\t\tRETURN
\t\t\tADDCOLUMNS(
\t\t\t\tCALENDAR(StartDate, EndDate),
\t\t\t\t"Year", YEAR([Date]),
\t\t\t\t"Year Quarter", FORMAT([Date], "YYYY") & " Q" & FORMAT([Date], "Q"),
\t\t\t\t"Quarter", "Q" & FORMAT([Date], "Q"),
\t\t\t\t"Quarter Number", QUARTER([Date]),
\t\t\t\t"Year Month", FORMAT([Date], "YYYY-MM"),
\t\t\t\t"Month Name", FORMAT([Date], "MMMM"),
\t\t\t\t"Month Short", FORMAT([Date], "MMM"),
\t\t\t\t"Month Number", MONTH([Date]),
\t\t\t\t"Week Start", [Date] - WEEKDAY([Date], 2) + 1,
\t\t\t\t"Week End", [Date] - WEEKDAY([Date], 2) + 7,
\t\t\t\t"Week Number", WEEKNUM([Date], 2),
\t\t\t\t"Year Week", FORMAT([Date], "YYYY") & "-W" & FORMAT(WEEKNUM([Date], 2), "00"),
\t\t\t\t"Day of Week", FORMAT([Date], "dddd"),
\t\t\t\t"Day of Week Short", FORMAT([Date], "ddd"),
\t\t\t\t"Day Number of Week", WEEKDAY([Date], 2),
\t\t\t\t"Is Past", IF([Date] <= TODAY(), TRUE(), FALSE()),
\t\t\t\t"Is Current Week", 
\t\t\t\t\tIF(
\t\t\t\t\t\t[Date] >= (TODAY() - WEEKDAY(TODAY(), 2) + 1) && 
\t\t\t\t\t\t[Date] <= (TODAY() - WEEKDAY(TODAY(), 2) + 7), 
\t\t\t\t\t\tTRUE(), 
\t\t\t\t\t\tFALSE()
\t\t\t\t\t),
\t\t\t\t"Relative Day Offset", DATEDIFF(TODAY(), [Date], DAY),
\t\t\t\t"Relative Week Offset", DATEDIFF(TODAY() - WEEKDAY(TODAY(), 2) + 1, [Date] - WEEKDAY([Date], 2) + 1, WEEK)
\t\t\t)
\t\t\t```
"""
    with open(tables_dir / "Calendar.tmdl", "w", encoding="utf-8") as f:
        f.write(calendar_tmdl)

    # 7. tables/Vulnerabilities.tmdl
    vuln_tmdl = """table Vulnerabilities

\tcolumn 'Device ID'
\t\tdataType: string
\t\tsourceColumn: aid

\tcolumn Hostname
\t\tdataType: string
\t\tsourceColumn: hostname

\tcolumn Platform
\t\tdataType: string
\t\tsourceColumn: platform_name

\tcolumn 'Vendor Normalized'
\t\tdataType: string
\t\tsourceColumn: app_vendor_normalized

\tcolumn Status
\t\tdataType: string
\t\tsourceColumn: status

\tcolumn 'Created Date'
\t\tdataType: dateTime
\t\tformatString: yyyy-mm-dd
\t\tsourceColumn: created_timestamp

\tcolumn 'Closed Date'
\t\tdataType: dateTime
\t\tformatString: yyyy-mm-dd
\t\tsourceColumn: closed_timestamp

\tcolumn 'CVE ID'
\t\tdataType: string
\t\tsourceColumn: cve_id

\tcolumn 'CVSS Base Score'
\t\tdataType: decimal
\t\tsourceColumn: cve_base_score

\tcolumn Severity
\t\tdataType: string
\t\tsourceColumn: cve_severity

\tcolumn is_cisa_kev
\t\tdataType: boolean
\t\tsourceColumn: is_cisa_kev

\tcolumn 'Last Reboot'
\t\tdataType: dateTime
\t\tsourceColumn: reporting_last_reboot

\tcolumn 'Vulnerability Age Days' = DATEDIFF('Vulnerabilities'[Created Date], TODAY(), DAY)
\t\tdataType: int64

\tcolumn 'Age Bucket' = ```
\t\tSWITCH(
\t\t\tTRUE(),
\t\t\t'Vulnerabilities'[Status] <> "Open", "Closed",
\t\t\t[Vulnerability Age Days] <= 30, "0-30 Days",
\t\t\t[Vulnerability Age Days] <= 60, "31-60 Days",
\t\t\t[Vulnerability Age Days] <= 90, "61-90 Days",
\t\t\t"90+ Days"
\t\t)
\t\t```
\t\tdataType: string

\tcolumn 'Device Patch Exception' = ```
\t\tVAR CutoffDate = TODAY() - 30
\t\tVAR LastMicrosoftClose =
\t\t\tCALCULATE(
\t\t\t\tMAX('Vulnerabilities'[Closed Date]),
\t\t\t\t'Vulnerabilities'[Platform] = "Windows",
\t\t\t\t'Vulnerabilities'[Vendor Normalized] = "Microsoft",
\t\t\t\t'Vulnerabilities'[Status] = "Closed",
\t\t\t\tREMOVEFILTERS('Calendar')
\t\t\t)
\t\tRETURN
\t\tIF(
\t\t\tSELECTEDVALUE('Vulnerabilities'[Platform]) = "Windows" && (
\t\t\t\tISBLANK(LastMicrosoftClose) || LastMicrosoftClose < CutoffDate
\t\t\t),
\t\t\t"Exception",
\t\t\t"Patched / Remediated"
\t\t)
\t\t```
\t\tdataType: string

\tpartition Vulnerabilities = m
\t\tmode: import
\t\tsource = ```
\t\t\tlet
\t\t\t\tSource = crowdstrike_vulnerability_device_reporting
\t\t\tin
\t\t\t\tSource
\t\t\t```
"""
    with open(tables_dir / "Vulnerabilities.tmdl", "w", encoding="utf-8") as f:
        f.write(vuln_tmdl)


def generate_pbir_report_definition(rep_dir: Path):
    """Generates the PBIR report layout and visual components."""
    def_dir = rep_dir / "definition"
    pages_dir = def_dir / "pages"
    page_id = "ExecDashboardPage01"
    page_dir = pages_dir / page_id
    vis_dir = page_dir / "visuals"
    vis_dir.mkdir(parents=True, exist_ok=True)

    # 1. definition.pbir
    pbir = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
        "version": "4.0",
        "datasetReference": {
            "byPath": {
                "path": "../CS_Dashboard.SemanticModel"
            }
        }
    }
    with open(rep_dir / "definition.pbir", "w", encoding="utf-8") as f:
        json.dump(pbir, f, indent=2)

    # 2. version.json
    with open(def_dir / "version.json", "w", encoding="utf-8") as f:
        json.dump({"version": "2.0.0"}, f, indent=2)

    # 3. report.json
    report_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.3.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "Fluent2-CY26SU08",
                "reportVersionAtImport": {
                    "visual": "2.12.0",
                    "report": "3.4.0",
                    "page": "2.3.1"
                },
                "type": "SharedResources"
            }
        },
        "settings": {
            "useStylableVisualContainerHeader": True,
            "exportDataMode": "AllowSummarized",
            "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True,
            "useEnhancedTooltips": True,
            "useDefaultAggregateDisplayName": True
        }
    }
    with open(def_dir / "report.json", "w", encoding="utf-8") as f:
        json.dump(report_json, f, indent=2)

    # 4. pages.json
    pages_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": [page_id],
        "activePageName": page_id
    }
    with open(pages_dir / "pages.json", "w", encoding="utf-8") as f:
        json.dump(pages_json, f, indent=2)

    # 5. page.json
    page_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": page_id,
        "displayName": "Executive Summary",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    }
    with open(page_dir / "page.json", "w", encoding="utf-8") as f:
        json.dump(page_json, f, indent=2)

    # Visual Helper
    def write_visual(v_id: str, obj: dict):
        v_path = vis_dir / v_id
        v_path.mkdir(parents=True, exist_ok=True)
        with open(v_path / "visual.json", "w", encoding="utf-8") as vf:
            json.dump(obj, vf, indent=2)

    # Visual 1: Title Banner Textbox
    v1_id = "v01_banner_title000"
    v1 = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": v1_id,
        "position": {"x": 30, "y": 20, "z": 100, "height": 70, "width": 1080, "tabOrder": 1},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [{
                                "value": "CrowdStrike Windows Vulnerability & Patch Compliance",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "22pt", "fontWeight": "bold", "color": {"solid": {"color": "#0F172A"}}}
                            }, {
                                "value": "\nExecutive Board Reporting | Scope: Windows OS + Microsoft Only",
                                "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "fontWeight": "normal", "color": {"solid": {"color": "#64748B"}}}
                            }]
                        }]
                    }
                }]
            }
        }
    }
    write_visual(v1_id, v1)

    # Visual 2: Platform Slicer
    v2_id = "v02_slicer_platform0"
    v2 = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": v2_id,
        "position": {"x": 1130, "y": 20, "z": 200, "height": 70, "width": 240, "tabOrder": 2},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Vulnerabilities"}}, "Property": "Platform"}},
                            "queryRef": "Vulnerabilities.Platform",
                            "nativeQueryRef": "Platform"
                        }]
                    }
                }
            }
        }
    }
    write_visual(v2_id, v2)

    # Visual 3: Scope Slicer (Vendor Normalized)
    v3_id = "v03_slicer_vendor000"
    v3 = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": v3_id,
        "position": {"x": 1390, "y": 20, "z": 300, "height": 70, "width": 240, "tabOrder": 3},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Vulnerabilities"}}, "Property": "Vendor Normalized"}},
                            "queryRef": "Vulnerabilities.Vendor Normalized",
                            "nativeQueryRef": "Vendor Normalized"
                        }]
                    }
                }
            }
        }
    }
    write_visual(v3_id, v3)

    # Visual 4: Week Slicer
    v4_id = "v04_slicer_weekstart"
    v4 = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": v4_id,
        "position": {"x": 1650, "y": 20, "z": 400, "height": 70, "width": 240, "tabOrder": 4},
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
    }
    write_visual(v4_id, v4)

    # KPI Helper Function
    def make_kpi_card(v_id: str, x: int, measure_name: str, label: str):
        return {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
            "name": v_id,
            "position": {"x": x, "y": 110, "z": 500, "height": 130, "width": 356, "tabOrder": 5},
            "visual": {
                "visualType": "cardVisual",
                "query": {
                    "queryState": {
                        "Data": {
                            "projections": [{
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": measure_name}},
                                "queryRef": f"_Measures.{measure_name}",
                                "nativeQueryRef": measure_name
                            }]
                        }
                    }
                }
            }
        }

    # Visual 5..9: Top 5 KPI Cards
    write_visual("v05_kpi_openvulns00", make_kpi_card("v05_kpi_openvulns00", 30, "Open Vulnerabilities", "Open In-Scope Vulnerabilities"))
    write_visual("v06_kpi_openover30d", make_kpi_card("v06_kpi_openover30d", 406, "Open Vulnerabilities >30 Days", "Open >30 Days SLA Breach"))
    write_visual("v07_kpi_cisakev0000", make_kpi_card("v07_kpi_cisakev0000", 782, "CISA KEV Vulnerabilities", "CISA KEV Active Exploits"))
    write_visual("v08_kpi_patchrate00", make_kpi_card("v08_kpi_patchrate00", 1158, "Patching Rate %", "30-Day Patching Compliance Rate"))
    write_visual("v09_kpi_devexcept00", make_kpi_card("v09_kpi_devexcept00", 1534, "Devices No Microsoft Remediation 30 Days", "Device Exceptions (>30d No Patch)"))

    # Visual 10: Weekly Trend Chart (Combo Chart)
    v10_id = "v10_trend_combo0000"
    v10 = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": v10_id,
        "position": {"x": 30, "y": 260, "z": 600, "height": 410, "width": 1150, "tabOrder": 10},
        "visual": {
            "visualType": "lineClusteredColumnComboChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Calendar"}}, "Property": "Week Start"}},
                            "queryRef": "Calendar.Week Start",
                            "nativeQueryRef": "Week Start"
                        }]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "New Vulnerabilities"}},
                                "queryRef": "_Measures.New Vulnerabilities",
                                "nativeQueryRef": "New Vulnerabilities"
                            },
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Closed Vulnerabilities by Closed Date"}},
                                "queryRef": "_Measures.Closed Vulnerabilities by Closed Date",
                                "nativeQueryRef": "Closed Vulnerabilities by Closed Date"
                            }
                        ]
                    },
                    "Y2": {
                        "projections": [{
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Net Vulnerability Change"}},
                            "queryRef": "_Measures.Net Vulnerability Change",
                            "nativeQueryRef": "Net Vulnerability Change"
                        }]
                    }
                }
            }
        }
    }
    write_visual(v10_id, v10)

    # Visual 11: Aging Buckets Bar Chart
    v11_id = "v11_aging_barchart0"
    v11 = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": v11_id,
        "position": {"x": 1200, "y": 260, "z": 700, "height": 410, "width": 690, "tabOrder": 11},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "Vulnerabilities"}}, "Property": "Age Bucket"}},
                            "queryRef": "Vulnerabilities.Age Bucket",
                            "nativeQueryRef": "Age Bucket"
                        }]
                    },
                    "Y": {
                        "projections": [{
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Open Vulnerabilities"}},
                            "queryRef": "_Measures.Open Vulnerabilities",
                            "nativeQueryRef": "Open Vulnerabilities"
                        }]
                    }
                }
            }
        }
    }
    write_visual(v11_id, v11)

    # Visual 12: Device & Vulnerability Operational Grid
    v12_id = "v12_detail_grid0000"
    v12 = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": v12_id,
        "position": {"x": 30, "y": 690, "z": 800, "height": 360, "width": 1860, "tabOrder": 12},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "Vulnerabilities"}}, "Property": "Hostname"}}, "queryRef": "Vulnerabilities.Hostname", "nativeQueryRef": "Hostname"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "Vulnerabilities"}}, "Property": "Device ID"}}, "queryRef": "Vulnerabilities.Device ID", "nativeQueryRef": "Device ID"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "Vulnerabilities"}}, "Property": "CVE ID"}}, "queryRef": "Vulnerabilities.CVE ID", "nativeQueryRef": "CVE ID"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "Vulnerabilities"}}, "Property": "Severity"}}, "queryRef": "Vulnerabilities.Severity", "nativeQueryRef": "Severity"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "Vulnerabilities"}}, "Property": "Created Date"}}, "queryRef": "Vulnerabilities.Created Date", "nativeQueryRef": "Created Date"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "Vulnerabilities"}}, "Property": "Closed Date"}}, "queryRef": "Vulnerabilities.Closed Date", "nativeQueryRef": "Closed Date"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "Vulnerabilities"}}, "Property": "Device Patch Exception"}}, "queryRef": "Vulnerabilities.Device Patch Exception", "nativeQueryRef": "Device Patch Exception"}
                        ]
                    }
                }
            },
            "objects": {
                "columnHeaders": [{
                    "properties": {
                        "columnAdjustment": {"expr": {"Literal": {"Value": "'growToFit'"}}},
                        "autoSizeColumnWidth": {"expr": {"Literal": {"Value": "true"}}}
                    }
                }]
            }
        }
    }
    write_visual(v12_id, v12)


def update_pbix_report(pbix_path: Path, rep_dir: Path):
    """Updates the internal Report/definition/ inside the PBIX file."""
    temp_pbix = pbix_path.with_suffix(".tmp.pbix")
    def_prefix = "Report/definition/"
    
    # Collect all new definition files
    new_files = {}
    for root, _, files in os.walk(rep_dir / "definition"):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(rep_dir / "definition")
            archive_path = f"Report/definition/{rel_path.as_posix()}"
            with open(full_path, "rb") as fh:
                new_files[archive_path] = fh.read()

    with zipfile.ZipFile(pbix_path, "r") as zin:
        with zipfile.ZipFile(temp_pbix, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if not item.filename.startswith(def_prefix):
                    zout.writestr(item, zin.read(item.filename))
            for arcname, data in new_files.items():
                zout.writestr(arcname, data)

    shutil.move(temp_pbix, pbix_path)
    print(f"Successfully updated {pbix_path} with {len(new_files)} report definition items.")


def main():
    print("=== Power BI Dashboard & PBIP Automation ===")
    out_dir = PBIP_TARGET_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Generate .pbip shortcut file
    pbip_file = out_dir / "CS_Dashboard.pbip"
    pbip_payload = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "CS_Dashboard.Report"
                }
            }
        ],
        "settings": {
            "enableAutoRecovery": True
        }
    }
    with open(pbip_file, "w", encoding="utf-8") as f:
        json.dump(pbip_payload, f, indent=2)

    # 2. Generate Semantic Model TMDL
    print("Generating TMDL Semantic Model...")
    generate_tmdl_definitions(out_dir)

    # 3. Generate PBIR Report Definition
    print("Generating PBIR Report Components...")
    rep_dir = out_dir / "CS_Dashboard.Report"
    generate_pbir_report_definition(rep_dir)

    # 4. Update the PBIX file directly
    if PBIX_PATH.exists():
        print(f"Updating PBIX archive at {PBIX_PATH}...")
        update_pbix_report(PBIX_PATH, rep_dir)

    print("Dashboard creation and compilation completed successfully!")


if __name__ == "__main__":
    main()
