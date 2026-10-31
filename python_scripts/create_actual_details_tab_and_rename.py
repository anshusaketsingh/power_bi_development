"""
create_actual_details_tab_and_rename.py

1. Renames p03_vulnerability_details displayName to 'Remediation Compliance'.
2. Creates p05_vulnerability_details ('Vulnerability Details') as the actual operational
   investigation matrix tab with granular CVE findings, full filter pane, KPI strip,
   and drillthrough bindings.
3. Updates Executive Summary navigation button to point to the new actual details tab.
4. Updates pages.json order.
"""

import json
import shutil
import time
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
REPORT = PROJ / "CS Dashboard.Report" / "definition"
PAGES_DIR = REPORT / "pages"
PAGES_JSON = PAGES_DIR / "pages.json"

TAB3_DIR = PAGES_DIR / "p03_vulnerability_details"
TAB5_DIR = PAGES_DIR / "p05_vulnerability_details"
EXEC_SUMMARY_DIR = PAGES_DIR / "47081098f92a957d7fd0"

VISUAL_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"
PAGE_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json"

DARK_GREEN = "#1b4332"
FACT = "crowdstrike_vulnerability_device_reporting"

def backup():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BASE_DIR / "development" / "jh_crowd_strike" / "backups" / f"pre_details_tab_create_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    if PAGES_JSON.exists():
        shutil.copy2(PAGES_JSON, dest / "pages.json")
    if TAB3_DIR.exists():
        shutil.copytree(TAB3_DIR, dest / "p03_vulnerability_details")
    print(f"Backup created at: {dest}")
    return dest

def lit(v):
    return {"expr": {"Literal": {"Value": v}}}

def color(hex_):
    return {"solid": {"color": lit(f"'{hex_}'")}}

def proj_col(table_name, col_name, native_name=None):
    return {
        "field": {
            "Column": {
                "Expression": {"SourceRef": {"Entity": table_name}},
                "Property": col_name
            }
        },
        "queryRef": f"{table_name}.{col_name}",
        "nativeQueryRef": native_name or col_name
    }

def proj_meas(meas_name, native_name=None):
    return {
        "field": {
            "Measure": {
                "Expression": {"SourceRef": {"Entity": "_Measures"}},
                "Property": meas_name
            }
        },
        "queryRef": f"_Measures.{meas_name}",
        "nativeQueryRef": native_name or meas_name
    }

def container_props(title=None, subtitle=None):
    c = {
        "border": [{"properties": {"show": lit("true"), "radius": lit("8D")}}],
        "background": [{"properties": {"show": lit("true"), "transparency": lit("0D")}}],
        "dropShadow": [{"properties": {"show": lit("true")}}]
    }
    if title:
        c["title"] = [{
            "properties": {
                "show": lit("true"),
                "text": lit(f"'{title}'"),
                "titleWrap": lit("true"),
                "fontColor": color(DARK_GREEN),
                "bold": lit("true"),
                "fontSize": lit("13D")
            }
        }]
    if subtitle:
        c["subTitle"] = [{
            "properties": {
                "show": lit("true"),
                "text": lit(f"'{subtitle}'")
            }
        }]
    return c

def rename_p03_to_remediation_compliance():
    page_json_file = TAB3_DIR / "page.json"
    if page_json_file.exists():
        data = json.loads(page_json_file.read_text(encoding="utf-8"))
        data["displayName"] = "Remediation Compliance"
        page_json_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print("  + Renamed p03 displayName to 'Remediation Compliance'")

def create_p05_page():
    TAB5_DIR.mkdir(parents=True, exist_ok=True)
    vis_dir = TAB5_DIR / "visuals"
    vis_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. page.json with full drillthrough configuration
    page_meta = {
        "$schema": PAGE_SCHEMA,
        "name": "p05_vulnerability_details",
        "displayName": "Vulnerability Details",
        "displayOption": "FitToPage",
        "height": 1080,
        "width": 1920,
        "filterConfig": {
            "filters": [
                {
                    "name": "Filter_Drill_cve_id",
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "cve_id"
                        }
                    },
                    "type": "Categorical",
                    "howCreated": "Drillthrough"
                },
                {
                    "name": "Filter_Drill_Age_Bucket",
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "Age Bucket"
                        }
                    },
                    "type": "Categorical",
                    "howCreated": "Drillthrough"
                },
                {
                    "name": "Filter_Drill_hostname",
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "reporting_hostname"
                        }
                    },
                    "type": "Categorical",
                    "howCreated": "Drillthrough"
                },
                {
                    "name": "Filter_Drill_Exception",
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "Device Patch Exception"
                        }
                    },
                    "type": "Categorical",
                    "howCreated": "Drillthrough"
                },
                {
                    "name": "Filter_Drill_Severity",
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "cve_severity"
                        }
                    },
                    "type": "Categorical",
                    "howCreated": "Drillthrough"
                },
                {
                    "name": "Filter_Drill_ExPRT",
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "ExPRT Rating"
                        }
                    },
                    "type": "Categorical",
                    "howCreated": "Drillthrough"
                }
            ]
        },
        "pageBinding": {
            "name": "Pod",
            "type": "Drillthrough",
            "parameters": [
                {
                    "name": "Param_Filter_Drill_cve_id",
                    "boundFilter": "Filter_Drill_cve_id",
                    "fieldExpr": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "cve_id"
                        }
                    }
                },
                {
                    "name": "Param_Filter_Drill_Age_Bucket",
                    "boundFilter": "Filter_Drill_Age_Bucket",
                    "fieldExpr": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "Age Bucket"
                        }
                    }
                },
                {
                    "name": "Param_Filter_Drill_hostname",
                    "boundFilter": "Filter_Drill_hostname",
                    "fieldExpr": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "reporting_hostname"
                        }
                    }
                },
                {
                    "name": "Param_Filter_Drill_Exception",
                    "boundFilter": "Filter_Drill_Exception",
                    "fieldExpr": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "Device Patch Exception"
                        }
                    }
                },
                {
                    "name": "Param_Filter_Drill_Severity",
                    "boundFilter": "Filter_Drill_Severity",
                    "fieldExpr": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "cve_severity"
                        }
                    }
                },
                {
                    "name": "Param_Filter_Drill_ExPRT",
                    "boundFilter": "Filter_Drill_ExPRT",
                    "fieldExpr": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": FACT}},
                            "Property": "ExPRT Rating"
                        }
                    }
                }
            ]
        },
        "objects": {
            "background": [
                {
                    "properties": {
                        "image": {
                            "image": {
                                "name": lit("'Untitled design.png'"),
                                "url": {
                                    "expr": {
                                        "ResourcePackageItem": {
                                            "PackageName": "RegisteredResources",
                                            "PackageType": 1,
                                            "ItemName": "Untitled_design844922143885944.png"
                                        }
                                    }
                                },
                                "scaling": lit("'Fit'")
                            }
                        },
                        "color": {
                            "solid": {
                                "color": {
                                    "expr": {
                                        "ThemeDataColor": {
                                            "ColorId": 0,
                                            "Percent": 0
                                        }
                                    }
                                }
                            }
                        },
                        "transparency": lit("0D")
                    }
                }
            ]
        }
    }
    (TAB5_DIR / "page.json").write_text(json.dumps(page_meta, indent=2), encoding="utf-8")
    
    # 2. Visuals for p05_vulnerability_details
    visuals = []
    
    # Logo
    visuals.append({
        "$schema": VISUAL_SCHEMA,
        "name": "p5_v00_logo_jh00000",
        "position": {"x": 35, "y": 18, "z": 0, "height": 80, "width": 260, "tabOrder": 0},
        "visual": {
            "visualType": "image",
            "objects": {
                "general": [{
                    "properties": {
                        "imageUrl": {
                            "expr": {
                                "ResourcePackageItem": {
                                    "PackageName": "RegisteredResources",
                                    "PackageType": 1,
                                    "ItemName": "James_Hardie_Logo20621795536914578.jpg"
                                }
                            }
                        }
                    }
                }],
                "imageScaling": [{"properties": {"imageScalingType": lit("'Fit'")}}]
            },
            "visualContainerObjects": {"background": [{"properties": {"show": lit("false")}}]}
        }
    })
    
    # Banner title
    visuals.append({
        "$schema": VISUAL_SCHEMA,
        "name": "p5_v01_banner_title",
        "position": {"x": 345, "y": 20, "z": 1000, "height": 80, "width": 1300, "tabOrder": 1000},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [
                            {
                                "textRuns": [{
                                    "value": "CrowdStrike Vulnerability Details & Investigation Matrix",
                                    "textStyle": {"fontWeight": "bold", "fontFamily": "Segoe UI", "fontSize": "21pt", "color": "#ffffff"}
                                }]
                            },
                            {
                                "textRuns": [{
                                    "value": "Granular Host & CVE Findings | Cross-Filtering, Drillthrough Context & Remediation Tracking",
                                    "textStyle": {"fontFamily": "Segoe UI", "fontSize": "11pt", "color": "#ffffff"}
                                }]
                            }
                        ]
                    }
                }]
            },
            "visualContainerObjects": {"background": [{"properties": {"show": lit("false")}}]}
        }
    })
    
    # Back to Executive button
    visuals.append({
        "$schema": VISUAL_SCHEMA,
        "name": "p5_btn_back",
        "position": {"x": 1670, "y": 32, "z": 2000, "height": 48, "width": 210, "tabOrder": 2000},
        "visual": {
            "visualType": "actionButton",
            "objects": {
                "text": [
                    {"properties": {"show": lit("true")}},
                    {
                        "properties": {
                            "text": lit("'<- Back to Executive'"),
                            "horizontalAlignment": lit("'center'"),
                            "fontColor": color(DARK_GREEN),
                            "bold": lit("true"),
                            "fontSize": lit("10D")
                        },
                        "selector": {"id": "default"}
                    }
                ],
                "shape": [
                    {"properties": {"roundEdge": lit("15L")}, "selector": {"id": "default"}}
                ],
                "fill": [
                    {"properties": {"show": lit("true"), "fillColor": color("#FFFFFF")}, "selector": {"id": "default"}}
                ]
            },
            "visualContainerObjects": {
                "visualLink": [{
                    "properties": {
                        "show": lit("true"),
                        "type": lit("'PageNavigation'"),
                        "navigationSection": lit("'47081098f92a957d7fd0'"),
                        "tooltipPlaceholderText": lit("'Return to Executive Summary'")
                    }
                }],
                "background": [{"properties": {"show": lit("false")}}]
            },
            "drillFilterOtherVisuals": True
        },
        "howCreated": "InsertVisualButton"
    })
    
    # KPI Strip: 4 KPI Cards
    kpis = [
        ("p5_kpi_open_total", 344.22, 128.13, 371.0, 118.57, "Open Vulnerabilities"),
        ("p5_kpi_crit_high", 734.34, 128.13, 371.0, 118.57, "Critical & High Vulnerabilities"),
        ("p5_kpi_cisa_kev", 1124.46, 128.13, 371.0, 118.57, "CISA KEV Vulnerabilities"),
        ("p5_kpi_patch_rate", 1514.58, 128.13, 371.0, 118.57, "Patching Rate %")
    ]
    for k_name, kx, ky, kw, kh, m_name in kpis:
        visuals.append({
            "$schema": VISUAL_SCHEMA,
            "name": k_name,
            "position": {"x": kx, "y": ky, "z": 3000, "height": kh, "width": kw, "tabOrder": 3000},
            "visual": {
                "visualType": "cardVisual",
                "query": {"queryState": {"Data": {"projections": [proj_meas(m_name)]}}},
                "objects": {"outline": [{"properties": {"show": lit("false")}, "selector": {"id": "default"}}]},
                "visualContainerObjects": container_props()
            }
        })
        
    # Slicers in Left Filter Pane
    slicers = [
        ("p5_slicer_week", 125, "Calendar", "Week Start"),
        ("p5_slicer_severity", 207, FACT, "cve_severity"),
        ("p5_slicer_exprt", 289, FACT, "ExPRT Rating"),
        ("p5_slicer_exception", 371, FACT, "Device Patch Exception"),
        ("p5_slicer_platform", 453, FACT, "Platform"),
        ("p5_slicer_cisakev", 535, FACT, "is_cisa_kev")
    ]
    for s_name, sy, tbl, prop in slicers:
        visuals.append({
            "$schema": VISUAL_SCHEMA,
            "name": s_name,
            "position": {"x": 28, "y": sy, "z": 4000, "height": 72, "width": 275, "tabOrder": 4000},
            "visual": {
                "visualType": "slicer",
                "query": {"queryState": {"Values": {"projections": [dict(proj_col(tbl, prop), active=True)]}}},
                "objects": {
                    "data": [{"properties": {"mode": lit("'Dropdown'")}}],
                    "header": [{"properties": {"show": lit("true"), "fontColor": color("#FFFFFF"), "textSize": lit("10D"), "bold": lit("true")}}],
                    "items": [{"properties": {"fontColor": color(DARK_GREEN), "background": color("#FFFFFF")}}]
                },
                "visualContainerObjects": {"background": [{"properties": {"show": lit("false")}}]}
            }
        })
        
    # Synced SLA Threshold Slicer at y=617
    visuals.append({
        "$schema": VISUAL_SCHEMA,
        "name": "p5_v13_slicer_sla_thresh",
        "position": {"x": 28, "y": 617, "z": 5000, "height": 72, "width": 275, "tabOrder": 5000},
        "visual": {
            "visualType": "slicer",
            "query": {"queryState": {"Values": {"projections": [dict(proj_col("SLA Threshold", "Threshold Days"), active=True)]}}},
            "objects": {
                "data": [
                    {"properties": {"mode": lit("'Dropdown'"), "isInvertedSelectionMode": lit("true")}}
                ],
                "header": [{"properties": {"show": lit("true"), "fontColor": color("#FFFFFF"), "textSize": lit("10D"), "bold": lit("true"), "text": lit("'SLA Threshold (1 - 365 Days)'")}}],
                "items": [{"properties": {"fontColor": color(DARK_GREEN), "background": color("#FFFFFF")}}],
                "selection": [{"properties": {"selectAllCheckboxEnabled": lit("true")}}]
            },
            "visualContainerObjects": {"background": [{"properties": {"show": lit("false")}}]},
            "syncGroup": {
                "groupName": "SLA Threshold",
                "fieldChanges": True,
                "filterChanges": True
            }
        }
    })
    
    # Clear All Slicers Button at y=980
    visuals.append({
        "$schema": VISUAL_SCHEMA,
        "name": "p5_btn_clear_slicers",
        "position": {"x": 55, "y": 980, "z": 6000, "height": 38, "width": 220, "tabOrder": 6000},
        "visual": {
            "visualType": "actionButton",
            "objects": {
                "icon": [
                    {"properties": {"shapeType": lit("'clearAllSlicers'")}, "selector": {"id": "default"}},
                    {"properties": {"show": lit("true"), "lineColor": color(DARK_GREEN)}}
                ],
                "text": [
                    {"properties": {"show": lit("true")}},
                    {
                        "properties": {
                            "text": lit("'Clear All Slicers'"),
                            "horizontalAlignment": lit("'center'"),
                            "fontColor": color(DARK_GREEN),
                            "bold": lit("true"),
                            "fontSize": lit("10D")
                        },
                        "selector": {"id": "default"}
                    }
                ],
                "shape": [{"properties": {"roundEdge": lit("18L")}, "selector": {"id": "default"}}],
                "fill": [{"properties": {"show": lit("true"), "fillColor": color("#FFFFFF")}, "selector": {"id": "default"}}]
            },
            "visualContainerObjects": {
                "visualLink": [{
                    "properties": {
                        "show": lit("true"),
                        "type": lit("'ClearAllSlicers'"),
                        "tooltipPlaceholderText": lit("'Clear all slicers on this page'")
                    }
                }],
                "background": [{"properties": {"show": lit("false")}}]
            },
            "drillFilterOtherVisuals": True
        },
        "howCreated": "InsertVisualButton"
    })
    
    # 3. The Actual Granular Operational Details Matrix (tableEx)
    visuals.append({
        "$schema": VISUAL_SCHEMA,
        "name": "p5_v02_detail_grid",
        "position": {
            "x": 344.2231075697211,
            "y": 258.1673306772908,
            "z": 10000,
            "height": 791.7131474103585,
            "width": 1541.3545816733067,
            "tabOrder": 10000
        },
        "visual": {
            "visualType": "tableEx",
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [
                            proj_col(FACT, "reporting_hostname", "Hostname"),
                            proj_col(FACT, "aid", "Device ID"),
                            proj_col(FACT, "reporting_os_version", "OS Version"),
                            proj_col(FACT, "cve_id", "CVE ID"),
                            proj_col(FACT, "cve_severity", "Severity"),
                            proj_col(FACT, "ExPRT Rating", "ExPRT Rating"),
                            proj_col(FACT, "Exploit Status", "Exploit Status"),
                            proj_col(FACT, "is_cisa_kev", "Is CISA KEV"),
                            proj_col(FACT, "Created Date", "Created Date"),
                            proj_col(FACT, "Vulnerability Age Days", "Age in Days"),
                            proj_col(FACT, "Device Patch Exception", "Patch Exception"),
                            proj_col(FACT, "status", "Status"),
                            proj_meas("Open Vulnerabilities", "Open Findings")
                        ]
                    }
                },
                "sortDefinition": {
                    "sort": [
                        {
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": FACT}},
                                    "Property": "Vulnerability Age Days"
                                }
                            },
                            "direction": "Descending"
                        }
                    ],
                    "isDefaultSort": True
                }
            },
            "objects": {
                "columnHeaders": [
                    {
                        "properties": {
                            "columnAdjustment": lit("'growToFit'"),
                            "autoSizeColumnWidth": lit("true"),
                            "fontColor": color("#FFFFFF"),
                            "backColor": color(DARK_GREEN),
                            "bold": lit("true"),
                            "fontSize": lit("11D")
                        }
                    }
                ],
                "grid": [
                    {
                        "properties": {
                            "rowPadding": lit("6D"),
                            "gridVertical": lit("false"),
                            "gridHorizontal": lit("true")
                        }
                    }
                ],
                "values": [
                    {
                        "properties": {
                            "fontSize": lit("10D")
                        }
                    }
                ]
            },
            "visualContainerObjects": container_props(
                "Active Vulnerability Operational Detail Matrix",
                "Granular device and CVE findings with drillthrough & cross-filter context"
            ),
            "drillFilterOtherVisuals": True
        }
    })
    
    # Save all visuals into p05_vulnerability_details/visuals/
    for v in visuals:
        v_folder = vis_dir / v["name"]
        v_folder.mkdir(parents=True, exist_ok=True)
        (v_folder / "visual.json").write_text(json.dumps(v, indent=2), encoding="utf-8")
        
    print(f"  + Created page 'p05_vulnerability_details' with {len(visuals)} visuals")

def update_pages_order():
    if not PAGES_JSON.exists():
        return
    data = json.loads(PAGES_JSON.read_text(encoding="utf-8"))
    order = data.get("pageOrder", [])
    
    # Insert p05_vulnerability_details right after p03_vulnerability_details
    if "p05_vulnerability_details" not in order:
        if "p03_vulnerability_details" in order:
            idx = order.index("p03_vulnerability_details") + 1
            order.insert(idx, "p05_vulnerability_details")
        else:
            order.append("p05_vulnerability_details")
            
    data["pageOrder"] = order
    PAGES_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"  + Updated pages.json pageOrder: {order}")

def update_executive_summary_nav_button():
    btn_file = EXEC_SUMMARY_DIR / "visuals" / "v20_btn_nav_details" / "visual.json"
    if not btn_file.exists():
        return
    data = json.loads(btn_file.read_text(encoding="utf-8"))
    try:
        data["visual"]["visualContainerObjects"]["visualLink"][0]["properties"]["navigationSection"] = lit("'p05_vulnerability_details'")
        btn_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print("  + Updated Executive Summary 'v20_btn_nav_details' to link to 'p05_vulnerability_details'")
    except Exception as e:
        print(f"  ! Nav button update skipped: {e}")

def main():
    print("=== Creating Actual Details Tab & Renaming Remediation Tab ===")
    backup()
    rename_p03_to_remediation_compliance()
    create_p05_page()
    update_pages_order()
    update_executive_summary_nav_button()
    print("=== Complete! ===")

if __name__ == "__main__":
    main()
