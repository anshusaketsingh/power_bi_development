"""
apply_model_and_visuals.py
Updates the user's unpackaged Power BI Project (CS Dashboard.pbip)
1. Enhances crowdstrike_vulnerability_device_reporting.tmdl with calculated columns.
2. Creates Calendar.tmdl (Monday Week Start) and _Measures.tmdl.
3. Creates relationships.tmdl (Active to Created Date, Inactive to Closed Date).
4. Updates model.tmdl to reference all tables.
5. Populates CS Dashboard.Report with all 12 executive visual containers.
"""

import os
import json
from pathlib import Path

BASE_DIR = Path("development/jh_crowd_strike/CS_Dashboard")
SEM_DIR = BASE_DIR / "CS Dashboard.SemanticModel"
REP_DIR = BASE_DIR / "CS Dashboard.Report"
DEF_DIR = SEM_DIR / "definition"
TABLES_DIR = DEF_DIR / "tables"

def update_semantic_model():
    print("Updating Semantic Model...")
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Update crowdstrike_vulnerability_device_reporting.tmdl with calculated columns
    main_table_file = TABLES_DIR / "crowdstrike_vulnerability_device_reporting.tmdl"
    with open(main_table_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Define calculated columns to append before the partition block
    calc_cols = """
\tcolumn 'Created Date' = DATEVALUE(LEFT('crowdstrike_vulnerability_device_reporting'[created_timestamp], 10))
\t\tdataType: dateTime
\t\tformatString: yyyy-mm-dd
\t\tsummarizeBy: none

\tcolumn 'Closed Date' = IF(NOT(ISBLANK('crowdstrike_vulnerability_device_reporting'[closed_timestamp])), DATEVALUE(LEFT('crowdstrike_vulnerability_device_reporting'[closed_timestamp], 10)))
\t\tdataType: dateTime
\t\tformatString: yyyy-mm-dd
\t\tsummarizeBy: none

\tcolumn Platform = 'crowdstrike_vulnerability_device_reporting'[reporting_platform]
\t\tdataType: string
\t\tsummarizeBy: none

\tcolumn 'Vendor Normalized' = ```
\t\tIF(
\t\t\tISBLANK('crowdstrike_vulnerability_device_reporting'[apps]) || 
\t\t\tCONTAINSSTRING(LOWER('crowdstrike_vulnerability_device_reporting'[apps]), "microsoft") || 
\t\t\tCONTAINSSTRING(LOWER('crowdstrike_vulnerability_device_reporting'[apps]), "windows"),
\t\t\t"Microsoft",
\t\t\tSWITCH(
\t\t\t\tTRUE(),
\t\t\t\tCONTAINSSTRING(LOWER('crowdstrike_vulnerability_device_reporting'[apps]), "google") || CONTAINSSTRING(LOWER('crowdstrike_vulnerability_device_reporting'[apps]), "chrome"), "Google",
\t\t\t\tCONTAINSSTRING(LOWER('crowdstrike_vulnerability_device_reporting'[apps]), "adobe"), "Adobe",
\t\t\t\tCONTAINSSTRING(LOWER('crowdstrike_vulnerability_device_reporting'[apps]), "oracle") || CONTAINSSTRING(LOWER('crowdstrike_vulnerability_device_reporting'[apps]), "java"), "Oracle",
\t\t\t\tCONTAINSSTRING(LOWER('crowdstrike_vulnerability_device_reporting'[apps]), "7-zip"), "7-Zip",
\t\t\t\t"Third-Party"
\t\t\t)
\t\t)
\t\t```
\t\tdataType: string
\t\tsummarizeBy: none

\tcolumn 'Vulnerability Age Days' = IF(NOT(ISBLANK('crowdstrike_vulnerability_device_reporting'[Created Date])), DATEDIFF('crowdstrike_vulnerability_device_reporting'[Created Date], TODAY(), DAY))
\t\tdataType: int64
\t\tsummarizeBy: none

\tcolumn 'Age Bucket' = ```
\t\tSWITCH(
\t\t\tTRUE(),
\t\t\t'crowdstrike_vulnerability_device_reporting'[status] <> "Open", "Closed",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 30, "0-30 Days",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 60, "31-60 Days",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 90, "61-90 Days",
\t\t\t"90+ Days"
\t\t)
\t\t```
\t\tdataType: string
\t\tsummarizeBy: none

\tcolumn 'Device Patch Exception' = ```
\t\tVAR CutoffDate = TODAY() - 30
\t\tVAR LastMicrosoftClose =
\t\t\tCALCULATE(
\t\t\t\tMAX('crowdstrike_vulnerability_device_reporting'[Closed Date]),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\tREMOVEFILTERS('Calendar')
\t\t\t)
\t\tRETURN
\t\tIF(
\t\t\tSELECTEDVALUE('crowdstrike_vulnerability_device_reporting'[Platform]) = "Windows" && (
\t\t\t\tISBLANK(LastMicrosoftClose) || LastMicrosoftClose < CutoffDate
\t\t\t),
\t\t\t"Exception",
\t\t\t"Patched / Remediated"
\t\t)
\t\t```
\t\tdataType: string
\t\tsummarizeBy: none
"""

    if "column 'Created Date'" not in content:
        # Insert calc_cols before partition
        part_idx = content.find("\tpartition crowdstrike_vulnerability_device_reporting")
        if part_idx != -1:
            updated_content = content[:part_idx] + calc_cols + "\n" + content[part_idx:]
        else:
            updated_content = content + "\n" + calc_cols
        with open(main_table_file, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print("Appended calculated columns to crowdstrike_vulnerability_device_reporting.tmdl")

    # 2. Create Calendar.tmdl
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
\t\t\tVAR MinFactDate = MIN('crowdstrike_vulnerability_device_reporting'[Created Date])
\t\t\tVAR MaxFactDate = MAXX(
\t\t\t\t'crowdstrike_vulnerability_device_reporting',
\t\t\t\tCOALESCE('crowdstrike_vulnerability_device_reporting'[Closed Date], 'crowdstrike_vulnerability_device_reporting'[Created Date])
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
    with open(TABLES_DIR / "Calendar.tmdl", "w", encoding="utf-8") as f:
        f.write(calendar_tmdl)
    print("Created Calendar.tmdl")

    # 3. Create _Measures.tmdl
    measures_tmdl = """table _Measures

\tmeasure 'In-Scope Vulnerabilities' = ```
\t\t// Total in-scope Microsoft Windows findings
\t\tCALCULATE(
\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft"
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'Open Vulnerabilities' = ```
\t\t// Current open Microsoft Windows findings
\t\tCALCULATE(
\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open"
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'Open Vulnerabilities >30 Days' = ```
\t\t// Open findings older than 30 days
\t\tVAR CutoffDate = TODAY() - 30
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

\tmeasure 'CISA KEV Vulnerabilities' = ```
\t\t// In-scope CISA KEV findings
\t\tCALCULATE(
\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t'crowdstrike_vulnerability_device_reporting'[is_cisa_kev] = TRUE()
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'CISA KEV %' = ```
\t\t// CISA KEV as percentage of open findings
\t\tDIVIDE([CISA KEV Vulnerabilities], [Open Vulnerabilities], 0)
\t\t```
\t\tformatString: 0.0%

\tmeasure 'Closed Vulnerabilities' = ```
\t\t// Total closed in filter context
\t\tCALCULATE(
\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed"
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'New Vulnerabilities' = ```
\t\t// New findings by period on Calendar
\t\tCALCULATE(
\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft"
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'Closed Vulnerabilities by Closed Date' = ```
\t\t// Closed findings activated via USERELATIONSHIP
\t\tCALCULATE(
\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\tUSERELATIONSHIP('Calendar'[Date], 'crowdstrike_vulnerability_device_reporting'[Closed Date])
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'Remediation Rate %' = ```
\t\tDIVIDE([Closed Vulnerabilities by Closed Date], [New Vulnerabilities], 0)
\t\t```
\t\tformatString: 0.0%

\tmeasure 'Net Vulnerability Change' = ```
\t\t[New Vulnerabilities] - [Closed Vulnerabilities by Closed Date]
\t\t```
\t\tformatString: +#,-#;0

\tmeasure 'Patching Rate %' = ```
\t\tVAR Closed30 = 
\t\t\tCALCULATE(
\t\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Closed Date] >= (TODAY() - 30)
\t\t\t)
\t\tVAR OpenOver30 = [Open Vulnerabilities >30 Days]
\t\tVAR Workload = Closed30 + OpenOver30
\t\tRETURN
\t\tDIVIDE(Closed30, Workload, 0)
\t\t```
\t\tformatString: 0.0%

\tmeasure 'Devices No Microsoft Remediation 30 Days' = ```
\t\tVAR CutoffDate = TODAY() - 30
\t\tRETURN
\t\tCOUNTROWS(
\t\t\tFILTER(
\t\t\t\tVALUES('crowdstrike_vulnerability_device_reporting'[aid]),
\t\t\t\tVAR LastMicrosoftClose =
\t\t\t\t\tCALCULATE(
\t\t\t\t\t\tMAX('crowdstrike_vulnerability_device_reporting'[Closed Date]),
\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
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
    with open(TABLES_DIR / "_Measures.tmdl", "w", encoding="utf-8") as f:
        f.write(measures_tmdl)
    print("Created _Measures.tmdl")

    # 4. Create relationships.tmdl (Clean, no ///)
    relationships_tmdl = """relationship 'Calendar to crowdstrike Created Date'
\tfromColumn: crowdstrike_vulnerability_device_reporting.'Created Date'
\ttoColumn: Calendar.Date

relationship 'Calendar to crowdstrike Closed Date'
\tisActive: false
\tfromColumn: crowdstrike_vulnerability_device_reporting.'Closed Date'
\ttoColumn: Calendar.Date
"""
    with open(DEF_DIR / "relationships.tmdl", "w", encoding="utf-8") as f:
        f.write(relationships_tmdl)
    print("Created relationships.tmdl")

    # 5. Update model.tmdl to reference Calendar and _Measures
    model_file = DEF_DIR / "model.tmdl"
    with open(model_file, "r", encoding="utf-8") as f:
        model_content = f.read()

    refs = []
    if "ref table Calendar" not in model_content:
        refs.append("ref table Calendar")
    if "ref table _Measures" not in model_content:
        refs.append("ref table _Measures")

    if refs:
        # Place refs before ref cultureInfo
        pos = model_content.find("ref cultureInfo")
        if pos != -1:
            new_model = model_content[:pos] + "\n".join(refs) + "\n\n" + model_content[pos:]
        else:
            new_model = model_content + "\n" + "\n".join(refs) + "\n"
        with open(model_file, "w", encoding="utf-8") as f:
            f.write(new_model)
        print("Updated model.tmdl with table refs")


def update_report_visuals():
    print("Updating Report Visuals...")
    pages_dir = REP_DIR / "definition" / "pages"
    
    # Read pages.json
    pages_json_file = pages_dir / "pages.json"
    with open(pages_json_file, "r", encoding="utf-8") as f:
        pages_meta = json.load(f)

    active_page_id = pages_meta.get("activePageName") or pages_meta["pageOrder"][0]
    page_dir = pages_dir / active_page_id
    page_file = page_dir / "page.json"

    # Update page display name and resolution (1920x1080)
    with open(page_file, "r", encoding="utf-8") as f:
        page_obj = json.load(f)
    page_obj["displayName"] = "Executive Summary"
    page_obj["height"] = 1080
    page_obj["width"] = 1920
    with open(page_file, "w", encoding="utf-8") as f:
        json.dump(page_obj, f, indent=2)

    vis_dir = page_dir / "visuals"
    vis_dir.mkdir(parents=True, exist_ok=True)

    def write_vis(v_id: str, obj: dict):
        p = vis_dir / v_id
        p.mkdir(parents=True, exist_ok=True)
        with open(p / "visual.json", "w", encoding="utf-8") as vf:
            json.dump(obj, vf, indent=2)

    # 1. Header Textbox
    write_vis("v01_banner_title000", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v01_banner_title000",
        "position": {"x": 30, "y": 20, "z": 100, "height": 70, "width": 1080, "tabOrder": 1},
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
                                    "value": "\nExecutive Board Reporting | Scope: Windows OS + Microsoft Only",
                                    "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "fontWeight": "normal", "color": {"solid": {"color": "#64748B"}}}
                                }
                            ]
                        }]
                    }
                }]
            }
        }
    })

    # 2. Platform Slicer
    write_vis("v02_slicer_platform0", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v02_slicer_platform0",
        "position": {"x": 1130, "y": 20, "z": 200, "height": 70, "width": 240, "tabOrder": 2},
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
        "position": {"x": 1390, "y": 20, "z": 300, "height": 70, "width": 240, "tabOrder": 3},
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
    })

    # KPI Cards (5)
    def make_kpi(v_id: str, x: int, measure_name: str):
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

    write_vis("v05_kpi_openvulns00", make_kpi("v05_kpi_openvulns00", 30, "Open Vulnerabilities"))
    write_vis("v06_kpi_openover30d", make_kpi("v06_kpi_openover30d", 406, "Open Vulnerabilities >30 Days"))
    write_vis("v07_kpi_cisakev0000", make_kpi("v07_kpi_cisakev0000", 782, "CISA KEV Vulnerabilities"))
    write_vis("v08_kpi_patchrate00", make_kpi("v08_kpi_patchrate00", 1158, "Patching Rate %"))
    write_vis("v09_kpi_devexcept00", make_kpi("v09_kpi_devexcept00", 1534, "Devices No Microsoft Remediation 30 Days"))

    # 10. Weekly Trend Combo Chart
    write_vis("v10_trend_combo0000", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v10_trend_combo0000",
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
    })

    # 11. Aging Buckets Clustered Column Chart
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
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Open Vulnerabilities"}},
                            "queryRef": "_Measures.Open Vulnerabilities",
                            "nativeQueryRef": "Open Vulnerabilities"
                        }]
                    }
                }
            }
        }
    })

    # 12. Detail Grid tableEx
    write_vis("v12_detail_grid0000", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v12_detail_grid0000",
        "position": {"x": 30, "y": 690, "z": 800, "height": 360, "width": 1860, "tabOrder": 12},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "reporting_hostname"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.reporting_hostname", "nativeQueryRef": "Hostname"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "aid"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.aid", "nativeQueryRef": "Device ID"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "cve_id"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.cve_id", "nativeQueryRef": "CVE ID"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "severity"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.severity", "nativeQueryRef": "Severity"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "Created Date"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.Created Date", "nativeQueryRef": "Created Date"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "Closed Date"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.Closed Date", "nativeQueryRef": "Closed Date"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "Device Patch Exception"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.Device Patch Exception", "nativeQueryRef": "Device Patch Exception"}
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
    })
    print("Successfully populated all 12 visual containers.")

def update_pbix_report():
    pbix_path = Path("development/jh_crowd_strike/CS Dashboard.pbix")
    if not pbix_path.exists():
        return
    import zipfile, shutil
    temp_pbix = pbix_path.with_suffix(".tmp.pbix")
    def_prefix = "Report/definition/"
    
    new_files = {}
    for root, _, files in os.walk(REP_DIR / "definition"):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(REP_DIR / "definition")
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
    print(f"Successfully synchronized PBIX file {pbix_path} with {len(new_files)} report definitions.")

def main():
    print("=== Applying Model and Visual Changes to Unpackaged PBIP ===")
    update_semantic_model()
    update_report_visuals()
    update_pbix_report()
    print("All updates successfully completed!")

if __name__ == "__main__":
    main()
