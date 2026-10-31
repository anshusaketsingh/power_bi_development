"""
add_second_tab_trends_and_exceptions.py
Adds a second report page/tab to CS Dashboard.Report:
"Trends & Device Exceptions" based on CrowdStrike_Windows_Patch_DAX_Business_Logic.docx:
1. Section 8: Weekly Remediation Rate % and Net Vulnerability Change Trend.
2. Section 9 & 10: Vulnerability Exposure by Severity and CISA KEV breakdown.
3. Section 6 & 7: Fleet Device Patch Exceptions Analysis ("Exception" vs "Patched / Remediated").
4. Section 12: Comprehensive Device Exception & Vulnerability Investigation Table.
Synchronizes both CS Dashboard.Report and CS Dashboard.pbix.
"""

import os
import json
from pathlib import Path

BASE_DIR = Path("development/jh_crowd_strike/CS_Dashboard")
REP_DIR = BASE_DIR / "CS Dashboard.Report"
PBIX_PATH = Path("development/jh_crowd_strike/CS Dashboard.pbix")

PAGES_DIR = REP_DIR / "definition" / "pages"
PAGES_JSON = PAGES_DIR / "pages.json"

def add_second_tab():
    print("1. Creating second tab in CS Dashboard.Report...")

    # Load existing pages.json
    with open(PAGES_JSON, "r", encoding="utf-8") as f:
        pages_meta = json.load(f)

    page2_id = "p02_trends_exceptions"
    if page2_id not in pages_meta["pageOrder"]:
        pages_meta["pageOrder"].append(page2_id)
        with open(PAGES_JSON, "w", encoding="utf-8") as f:
            json.dump(pages_meta, f, indent=2)
        print(f"Added {page2_id} to pages.json")

    # Create page directory
    p2_dir = PAGES_DIR / page2_id
    p2_dir.mkdir(parents=True, exist_ok=True)
    vis_dir = p2_dir / "visuals"
    vis_dir.mkdir(parents=True, exist_ok=True)

    # 1. page.json
    page_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": page2_id,
        "displayName": "Trends & Device Exceptions",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920
    }
    with open(p2_dir / "page.json", "w", encoding="utf-8") as f:
        json.dump(page_json, f, indent=2)

    def write_vis(v_id: str, obj: dict):
        p = vis_dir / v_id
        p.mkdir(parents=True, exist_ok=True)
        with open(p / "visual.json", "w", encoding="utf-8") as vf:
            json.dump(obj, vf, indent=2)

    # Visual 1: Header Textbox
    write_vis("p2_v01_banner_title", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p2_v01_banner_title",
        "position": {"x": 30, "y": 20, "z": 100, "height": 70, "width": 1050, "tabOrder": 1},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [
                                {
                                    "value": "Vulnerability Trends & Device Patch Exceptions",
                                    "textStyle": {"fontFamily": "Segoe UI", "fontSize": "22pt", "fontWeight": "bold", "color": {"solid": {"color": "#0F172A"}}}
                                },
                                {
                                    "value": "\nGranular Weekly Remediation Dynamics, Severity Exposure & 30-Day Fleet Exceptions",
                                    "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "fontWeight": "normal", "color": {"solid": {"color": "#64748B"}}}
                                }
                            ]
                        }]
                    }
                }]
            }
        }
    })

    # Visual 2: Week Start Slicer
    write_vis("p2_v02_slicer_week", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p2_v02_slicer_week",
        "position": {"x": 1100, "y": 20, "z": 200, "height": 70, "width": 250, "tabOrder": 2},
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

    # Visual 3: Severity Slicer
    write_vis("p2_v03_slicer_severity", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p2_v03_slicer_severity",
        "position": {"x": 1370, "y": 20, "z": 300, "height": 70, "width": 250, "tabOrder": 3},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "severity"}},
                            "queryRef": "crowdstrike_vulnerability_device_reporting.severity",
                            "nativeQueryRef": "Severity"
                        }]
                    }
                }
            }
        }
    })

    # Visual 4: Device Exception Slicer
    write_vis("p2_v04_slicer_exception", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p2_v04_slicer_exception",
        "position": {"x": 1640, "y": 20, "z": 400, "height": 70, "width": 250, "tabOrder": 4},
        "visual": {
            "visualType": "slicer",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "Device Patch Exception"}},
                            "queryRef": "crowdstrike_vulnerability_device_reporting.Device Patch Exception",
                            "nativeQueryRef": "Device Patch Exception"
                        }]
                    }
                }
            }
        }
    })

    # Visual 5 (Chart 1): Weekly Remediation Rate % & Net Change Trend (Section 8)
    write_vis("p2_v05_trend_remed_rate", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p2_v05_trend_remed_rate",
        "position": {"x": 30, "y": 110, "z": 500, "height": 430, "width": 620, "tabOrder": 5},
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
                        "projections": [{
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Net Vulnerability Change"}},
                            "queryRef": "_Measures.Net Vulnerability Change",
                            "nativeQueryRef": "Net Vulnerability Change"
                        }]
                    },
                    "Y2": {
                        "projections": [{
                            "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Remediation Rate %"}},
                            "queryRef": "_Measures.Remediation Rate %",
                            "nativeQueryRef": "Remediation Rate %"
                        }]
                    }
                }
            }
        }
    })

    # Visual 6 (Chart 2): Open Vulnerabilities by Severity & CISA KEV (Section 10)
    write_vis("p2_v06_bar_severity_kev", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p2_v06_bar_severity_kev",
        "position": {"x": 670, "y": 110, "z": 600, "height": 430, "width": 600, "tabOrder": 6},
        "visual": {
            "visualType": "clusteredBarChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "severity"}},
                            "queryRef": "crowdstrike_vulnerability_device_reporting.severity",
                            "nativeQueryRef": "Severity"
                        }]
                    },
                    "Y": {
                        "projections": [
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "Open Vulnerabilities"}},
                                "queryRef": "_Measures.Open Vulnerabilities",
                                "nativeQueryRef": "Open Vulnerabilities"
                            },
                            {
                                "field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": "CISA KEV Vulnerabilities"}},
                                "queryRef": "_Measures.CISA KEV Vulnerabilities",
                                "nativeQueryRef": "CISA KEV Vulnerabilities"
                            }
                        ]
                    }
                }
            }
        }
    })

    # Visual 7 (Chart 3): Fleet Device Patch Exception Breakdown (Section 6 & 7)
    write_vis("p2_v07_bar_device_exceptions", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p2_v07_bar_device_exceptions",
        "position": {"x": 1290, "y": 110, "z": 700, "height": 430, "width": 600, "tabOrder": 7},
        "visual": {
            "visualType": "clusteredColumnChart",
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{
                            "field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "Device Patch Exception"}},
                            "queryRef": "crowdstrike_vulnerability_device_reporting.Device Patch Exception",
                            "nativeQueryRef": "Device Patch Exception"
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

    # Visual 8: Device & Vulnerability Investigation Table (Section 12)
    write_vis("p2_v08_grid_investigation", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p2_v08_grid_investigation",
        "position": {"x": 30, "y": 560, "z": 800, "height": 490, "width": 1860, "tabOrder": 8},
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "reporting_hostname"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.reporting_hostname", "nativeQueryRef": "Hostname"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "aid"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.aid", "nativeQueryRef": "Device ID (AID)"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "reporting_os_version"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.reporting_os_version", "nativeQueryRef": "OS Version"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "reporting_last_seen"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.reporting_last_seen", "nativeQueryRef": "Last Seen"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "reporting_last_reboot"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.reporting_last_reboot", "nativeQueryRef": "Last Reboot"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "cve_id"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.cve_id", "nativeQueryRef": "CVE ID"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "severity"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.severity", "nativeQueryRef": "Severity"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "is_cisa_kev"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.is_cisa_kev", "nativeQueryRef": "Is CISA KEV"},
                            {"field": {"Column": {"Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}}, "Property": "Device Patch Exception"}}, "queryRef": "crowdstrike_vulnerability_device_reporting.Device Patch Exception", "nativeQueryRef": "Patch Exception"}
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

    print(f"Successfully generated all visuals for page 2 ({page2_id}).")

def sync_pbix():
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
    print(f"Synchronized PBIX archive {PBIX_PATH} with 2 pages and all visuals.")

def main():
    print("=== Adding Second Tab: Trends & Device Exceptions ===")
    add_second_tab()
    sync_pbix()
    print("All tasks completed successfully!")

if __name__ == "__main__":
    main()
