#!/usr/bin/env python3
"""
move_details_to_drillthrough_tab.py
Moves the granular operational details matrix from Executive Summary to a dedicated
Drillthrough tab ('Vulnerability Details' - p03_vulnerability_details), and adjusts
the Executive Summary visuals to fill the freed space with high-impact executive charts.

Key updates:
1. Creates 'p03_vulnerability_details' page with drillthrough filters for:
   - cve_id
   - Severity
   - Age Bucket
   - reporting_hostname
   - Device Patch Exception
2. Configures 'Vulnerability Details' page with:
   - Company template background (Untitled_design) & JH logo
   - 'Back to Executive' navigation button
   - Left-side filter pane
   - Summary KPI strip (Scope, Crit/High, KEV, Remediation %)
   - Expansive granular operational detail grid (height=815px, width=1540px)
3. Updates Executive Summary ('47081098f92a957d7fd0'):
   - Removes detail grid from Tab 1
   - Balances Row 2: Trend combo chart (w=960, h=375) + Dynamic SLA aging chart (w=560, h=375)
   - Fills Row 3 (y=660, h=390):
     * Top Microsoft CVEs by Open Volume (w=960, h=390) - prime drillthrough launchpad
     * Open Vulnerabilities by Severity & CISA KEV (w=560, h=390)
   - Adds drillthrough link button in the header ('View Granular Details ->')
4. Updates pages.json pageOrder.
5. Synchronizes CS Dashboard.pbix archive.
"""

import os
import shutil
import json
import zipfile
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
TARGET_REP = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard" / "CS Dashboard.Report"
PBIX_PATH = BASE_DIR / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"

def update_pages_order():
    print("--- 1. Updating pages.json with 'p03_vulnerability_details' ---")
    pages_json_path = TARGET_REP / "definition" / "pages" / "pages.json"
    pages_def = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.1.0/schema.json",
        "pageOrder": [
            "47081098f92a957d7fd0",
            "p02_trends_exceptions",
            "p03_vulnerability_details"
        ],
        "activePageName": "47081098f92a957d7fd0"
    }
    with open(pages_json_path, "w", encoding="utf-8") as f:
        json.dump(pages_def, f, indent=2)
    print("  pages.json updated.")

def create_tab3_drillthrough_page():
    print("--- 2. Creating Tab 3 'Vulnerability Details' page.json with Drillthrough bindings ---")
    p3_dir = TARGET_REP / "definition" / "pages" / "p03_vulnerability_details"
    p3_dir.mkdir(parents=True, exist_ok=True)
    p3_vis_dir = p3_dir / "visuals"
    p3_vis_dir.mkdir(parents=True, exist_ok=True)

    page_def = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
        "name": "p03_vulnerability_details",
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
                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
                            "Property": "cve_id"
                        }
                    },
                    "type": "Categorical",
                    "howCreated": "Drillthrough"
                },
                {
                    "name": "Filter_Drill_Severity",
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
                            "Property": "Severity"
                        }
                    },
                    "type": "Categorical",
                    "howCreated": "Drillthrough"
                },
                {
                    "name": "Filter_Drill_Age_Bucket",
                    "field": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
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
                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
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
                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
                            "Property": "Device Patch Exception"
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
                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
                            "Property": "cve_id"
                        }
                    }
                },
                {
                    "name": "Param_Filter_Drill_Severity",
                    "boundFilter": "Filter_Drill_Severity",
                    "fieldExpr": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
                            "Property": "Severity"
                        }
                    }
                },
                {
                    "name": "Param_Filter_Drill_Age_Bucket",
                    "boundFilter": "Filter_Drill_Age_Bucket",
                    "fieldExpr": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
                            "Property": "Age Bucket"
                        }
                    }
                },
                {
                    "name": "Param_Filter_Drill_hostname",
                    "boundFilter": "Filter_Drill_hostname",
                    "fieldExpr": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
                            "Property": "reporting_hostname"
                        }
                    }
                },
                {
                    "name": "Param_Filter_Drill_Exception",
                    "boundFilter": "Filter_Drill_Exception",
                    "fieldExpr": {
                        "Column": {
                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
                            "Property": "Device Patch Exception"
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
                                "name": {"expr": {"Literal": {"Value": "'Untitled design.png'"}}},
                                "url": {
                                    "expr": {
                                        "ResourcePackageItem": {
                                            "PackageName": "RegisteredResources",
                                            "PackageType": 1,
                                            "ItemName": "Untitled_design844922143885944.png"
                                        }
                                    }
                                },
                                "scaling": {"expr": {"Literal": {"Value": "'Fit'"}}}
                            }
                        },
                        "color": {"solid": {"color": {"expr": {"ThemeDataColor": {"ColorId": 0, "Percent": 0}}}}},
                        "transparency": {"expr": {"Literal": {"Value": "0D"}}}
                    }
                }
            ]
        }
    }
    with open(p3_dir / "page.json", "w", encoding="utf-8") as f:
        json.dump(page_def, f, indent=2)
    print("  Tab 3 page.json created with Drillthrough bindings.")

def setup_tab3_visuals():
    print("--- 3. Setting up Tab 3 visuals ---")
    p3_vis_dir = TARGET_REP / "definition" / "pages" / "p03_vulnerability_details" / "visuals"

    # Helper for writing visuals
    def write_vis(name, data):
        vdir = p3_vis_dir / name
        vdir.mkdir(parents=True, exist_ok=True)
        with open(vdir / "visual.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    # 1. Logo: x=35, y=18, w=260, h=80
    write_vis("p3_v00_logo_jh00000", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p3_v00_logo_jh00000",
        "position": {"x": 35, "y": 18, "z": 50, "height": 80, "width": 260, "tabOrder": 0},
        "visual": {
            "visualType": "image",
            "objects": {
                "general": [{"properties": {"imageUrl": {"expr": {"ResourcePackageItem": {"PackageName": "RegisteredResources", "PackageType": 1, "ItemName": "James_Hardie_Logo20621795536914578.jpg"}}}}}],
                "imageScaling": [{"properties": {"imageScalingType": {"expr": {"Literal": {"Value": "'Fit'"}}}}}]
            },
            "drillFilterOtherVisuals": True
        },
        "howCreated": "InsertVisualButton"
    })

    # 2. Title: x=345, y=20, w=1300, h=80
    write_vis("p3_v01_banner_title", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p3_v01_banner_title",
        "position": {"x": 345, "y": 20, "z": 100, "height": 80, "width": 1300, "tabOrder": 1},
        "visual": {
            "visualType": "textbox",
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": "CrowdStrike Vulnerability & Device Details",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "21pt",
                                                "fontWeight": "bold",
                                                "color": {"solid": {"color": "#FFFFFF"}}
                                            }
                                        },
                                        {
                                            "value": "\nGranular Operational Investigation Matrix | Drillthrough & Filtering Enabled",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "11pt",
                                                "fontWeight": "normal",
                                                "color": {"solid": {"color": "#C6E2D1"}}
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            },
            "visualContainerObjects": {
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            }
        }
    })

    # 3. Back Button: x=1670, y=32, w=210, h=48
    write_vis("p3_btn_back", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p3_btn_back",
        "position": {"x": 1670, "y": 32, "z": 5000, "height": 48, "width": 210, "tabOrder": 95},
        "visual": {
            "visualType": "actionButton",
            "objects": {
                "icon": [
                    {
                        "properties": {"shapeType": {"expr": {"Literal": {"Value": "'back'"}}}},
                        "selector": {"id": "default"}
                    },
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1b4332'"}}}}}
                        }
                    }
                ],
                "text": [
                    {"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}},
                    {
                        "properties": {
                            "text": {"expr": {"Literal": {"Value": "'<- Back to Summary'"}}},
                            "horizontalAlignment": {"expr": {"Literal": {"Value": "'center'"}}},
                            "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1b4332'"}}}}},
                            "bold": {"expr": {"Literal": {"Value": "true"}}},
                            "fontSize": {"expr": {"Literal": {"Value": "10D"}}}
                        },
                        "selector": {"id": "default"}
                    }
                ],
                "shape": [
                    {"properties": {"roundEdge": {"expr": {"Literal": {"Value": "15L"}}}}, "selector": {"id": "default"}}
                ],
                "fill": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "fillColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}
                        },
                        "selector": {"id": "default"}
                    }
                ]
            },
            "visualContainerObjects": {
                "visualLink": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "type": {"expr": {"Literal": {"Value": "'Back'"}}},
                            "tooltipPlaceholderText": {"expr": {"Literal": {"Value": "'Return to previous page'"}}}
                        }
                    }
                ],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        },
        "howCreated": "InsertVisualButton"
    })

    # 4. Slicers on Left Filter Shelf
    def make_slicer(vname, x, y, w, h, table, col, to):
        return {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
            "name": vname,
            "position": {"x": x, "y": y, "z": 200+to, "height": h, "width": w, "tabOrder": to},
            "visual": {
                "visualType": "slicer",
                "query": {"queryState": {"Values": {"projections": [{"field": {"Column": {"Expression": {"SourceRef": {"Entity": table}}, "Property": col}}, "queryRef": f"{table}.{col}", "nativeQueryRef": col}]}}},
                "objects": {
                    "data": [{"properties": {"mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}}}],
                    "header": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "textSize": {"expr": {"Literal": {"Value": "10D"}}}, "bold": {"expr": {"Literal": {"Value": "true"}}}}}],
                    "items": [{"properties": {"fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1b4332'"}}}}}, "background": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}}}]
                },
                "visualContainerObjects": {"background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]}
            }
        }

    slicers = [
        ("p3_slicer_week", 125, "Calendar", "Week Start", 2),
        ("p3_slicer_severity", 207, "crowdstrike_vulnerability_device_reporting", "Severity", 3),
        ("p3_slicer_exception", 289, "crowdstrike_vulnerability_device_reporting", "Device Patch Exception", 4),
        ("p3_slicer_platform", 371, "crowdstrike_vulnerability_device_reporting", "Platform", 5),
        ("p3_slicer_cisakev", 453, "crowdstrike_vulnerability_device_reporting", "is_cisa_kev", 6),
        ("p3_slicer_sla_thresh", 535, "SLA Threshold", "Threshold Label", 7),
    ]
    for vname, y, tbl, col, to in slicers:
        write_vis(vname, make_slicer(vname, 28, y, 275, 72, tbl, col, to))

    # Clear Slicers Button
    write_vis("p3_btn_clear_slicers", {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p3_btn_clear_slicers",
        "position": {"x": 55, "y": 980, "z": 6000, "height": 38, "width": 220, "tabOrder": 90},
        "visual": {
            "visualType": "actionButton",
            "objects": {
                "icon": [{"properties": {"shapeType": {"expr": {"Literal": {"Value": "'clearAllSlicers'"}}}}, "selector": {"id": "default"}}, {"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "lineColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1b4332'"}}}}}}}],
                "text": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}}, {"properties": {"text": {"expr": {"Literal": {"Value": "'Clear All Slicers'"}}}, "horizontalAlignment": {"expr": {"Literal": {"Value": "'center'"}}}, "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1b4332'"}}}}}, "bold": {"expr": {"Literal": {"Value": "true"}}}, "fontSize": {"expr": {"Literal": {"Value": "10D"}}}}, "selector": {"id": "default"}}],
                "shape": [{"properties": {"roundEdge": {"expr": {"Literal": {"Value": "18L"}}}}, "selector": {"id": "default"}}],
                "fill": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "fillColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "selector": {"id": "default"}}}]
            },
            "visualContainerObjects": {
                "visualLink": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "type": {"expr": {"Literal": {"Value": "'ClearAllSlicers'"}}}, "tooltipPlaceholderText": {"expr": {"Literal": {"Value": "'Clear all filters on this page'"}}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
            },
            "drillFilterOtherVisuals": True
        },
        "howCreated": "InsertVisualButton"
    })

    # 5. Summary KPI Strip across content top (y=125, h=95, w=365 each, 4 cards across 1540px)
    kpis = [
        ("p3_kpi_open_total", 345, "Open Vulnerabilities", "Total Open Findings in Scope"),
        ("p3_kpi_crit_high", 735, "Critical & High Vulnerabilities", "Critical & High Severity Findings"),
        ("p3_kpi_cisa_kev", 1125, "CISA KEV Vulnerabilities", "CISA Known Exploited (KEV)"),
        ("p3_kpi_patch_rate", 1515, "Patch Remediated %", "Remediation Rate %"),
    ]
    for vname, x, meas, title in kpis:
        write_vis(vname, {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
            "name": vname,
            "position": {"x": x, "y": 125, "z": 500, "height": 95, "width": 370, "tabOrder": 10},
            "visual": {
                "visualType": "cardVisual",
                "query": {"queryState": {"Data": {"projections": [{"field": {"Measure": {"Expression": {"SourceRef": {"Entity": "_Measures"}}, "Property": meas}}, "queryRef": f"_Measures.{meas}", "nativeQueryRef": meas}]}}},
                "visualContainerObjects": {
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                    "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": f"'{title}'"}}}, "titleWrap": {"expr": {"Literal": {"Value": "true"}}}}}]
                }
            }
        })

    # 6. Granular Operational Detail Grid: x=345, y=235, w=1540, h=815
    # Read columns from original grid
    orig_grid_path = TARGET_REP / "definition" / "pages" / "47081098f92a957d7fd0" / "visuals" / "v12_detail_grid0000" / "visual.json"
    if orig_grid_path.exists():
        with open(orig_grid_path, "r", encoding="utf-8") as f:
            grid_def = json.load(f)
    else:
        grid_def = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.10.0/schema.json",
            "visual": {"visualType": "tableEx"}
        }
    
    grid_def["name"] = "p3_v02_detail_grid"
    grid_def["position"] = {"x": 345, "y": 235, "z": 800, "height": 815, "width": 1540, "tabOrder": 30}
    grid_def.setdefault("visual", {})["visualContainerObjects"] = {
        "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}],
        "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
        "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": "'Active Microsoft Vulnerability Matrix (Drillthrough Filtered)'"}}}, "titleWrap": {"expr": {"Literal": {"Value": "true"}}}}}]
    }
    write_vis("p3_v02_detail_grid", grid_def)
    print("  Tab 3 visuals successfully created.")

def adjust_executive_summary():
    print("--- 4. Adjusting Executive Summary visuals to fill space seamlessly ---")
    p1_vis_dir = TARGET_REP / "definition" / "pages" / "47081098f92a957d7fd0" / "visuals"

    # Remove detail grid from Executive Summary
    old_grid_dir = p1_vis_dir / "v12_detail_grid0000"
    if old_grid_dir.exists():
        shutil.rmtree(old_grid_dir)
        print("  Removed 'v12_detail_grid0000' from Executive Summary.")

    # Add Drillthrough Navigation Button in Header: x=1680, y=35, w=195, h=45
    btn_nav_dir = p1_vis_dir / "v20_btn_nav_details"
    btn_nav_dir.mkdir(parents=True, exist_ok=True)
    with open(btn_nav_dir / "visual.json", "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
            "name": "v20_btn_nav_details",
            "position": {"x": 1680, "y": 32, "z": 5000, "height": 48, "width": 205, "tabOrder": 95},
            "visual": {
                "visualType": "actionButton",
                "objects": {
                    "text": [
                        {"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}}},
                        {
                            "properties": {
                                "text": {"expr": {"Literal": {"Value": "'Vulnerability Details ->'"}}},
                                "horizontalAlignment": {"expr": {"Literal": {"Value": "'center'"}}},
                                "fontColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#1b4332'"}}}}},
                                "bold": {"expr": {"Literal": {"Value": "true"}}},
                                "fontSize": {"expr": {"Literal": {"Value": "10D"}}}
                            },
                            "selector": {"id": "default"}
                        }
                    ],
                    "shape": [{"properties": {"roundEdge": {"expr": {"Literal": {"Value": "15L"}}}}, "selector": {"id": "default"}}],
                    "fill": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "fillColor": {"solid": {"color": {"expr": {"Literal": {"Value": "'#FFFFFF'"}}}}}, "selector": {"id": "default"}}}]
                },
                "visualContainerObjects": {
                    "visualLink": [
                        {
                            "properties": {
                                "show": {"expr": {"Literal": {"Value": "true"}}},
                                "type": {"expr": {"Literal": {"Value": "'PageNavigation'"}}},
                                "navigationSection": {"expr": {"Literal": {"Value": "'p03_vulnerability_details'"}}},
                                "tooltipPlaceholderText": {"expr": {"Literal": {"Value": "'Navigate to granular vulnerability details'"}}}
                            }
                        }
                    ],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "false"}}}}}]
                },
                "drillFilterOtherVisuals": True
            },
            "howCreated": "InsertVisualButton"
        }, f, indent=2)
    print("  Added 'v20_btn_nav_details' navigation button on Executive Summary.")

    # Re-align Row 2 (Charts): y=265, h=375
    # Combo chart: x=345, w=960, h=375
    combo_path = p1_vis_dir / "v10_trend_combo0000" / "visual.json"
    if combo_path.exists():
        with open(combo_path, "r", encoding="utf-8") as f:
            cdef = json.load(f)
        cdef["position"] = {"x": 345, "y": 265, "z": 700, "height": 375, "width": 960, "tabOrder": 20}
        with open(combo_path, "w", encoding="utf-8") as f:
            json.dump(cdef, f, indent=2)

    # Aging chart: x=1325, w=560, h=375
    aging_path = p1_vis_dir / "v11_aging_barchart0" / "visual.json"
    if aging_path.exists():
        with open(aging_path, "r", encoding="utf-8") as f:
            adef = json.load(f)
        adef["position"] = {"x": 1325, "y": 265, "z": 700, "height": 375, "width": 560, "tabOrder": 21}
        with open(aging_path, "w", encoding="utf-8") as f:
            json.dump(adef, f, indent=2)

    # Fill Row 3 (y=660, h=390):
    # Visual 1: Top Microsoft CVEs by Affected Devices (clusteredBarChart)
    top_cve_dir = p1_vis_dir / "v18_bar_top_cves"
    top_cve_dir.mkdir(parents=True, exist_ok=True)
    with open(top_cve_dir / "visual.json", "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
            "name": "v18_bar_top_cves",
            "position": {"x": 345, "y": 660, "z": 700, "height": 390, "width": 960, "tabOrder": 30},
            "visual": {
                "visualType": "clusteredBarChart",
                "query": {
                    "queryState": {
                        "Category": {
                            "projections": [
                                {
                                    "field": {
                                        "Column": {
                                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
                                            "Property": "cve_id"
                                        }
                                    },
                                    "queryRef": "crowdstrike_vulnerability_device_reporting.cve_id",
                                    "nativeQueryRef": "cve_id",
                                    "active": True
                                }
                            ]
                        },
                        "Y": {
                            "projections": [
                                {
                                    "field": {
                                        "Measure": {
                                            "Expression": {"SourceRef": {"Entity": "_Measures"}},
                                            "Property": "Open Vulnerabilities"
                                        }
                                    },
                                    "queryRef": "_Measures.Open Vulnerabilities",
                                    "nativeQueryRef": "Open Vulnerabilities"
                                }
                            ]
                        }
                    },
                    "sortDefinition": {
                        "sort": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {"SourceRef": {"Entity": "_Measures"}},
                                        "Property": "Open Vulnerabilities"
                                    }
                                },
                                "direction": "Descending"
                            }
                        ]
                    }
                },
                "visualContainerObjects": {
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                    "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": "'Top Microsoft CVEs by Open Volume (Right-click to Drill Through)'"}}}, "titleWrap": {"expr": {"Literal": {"Value": "true"}}}}}]
                }
            }
        }, f, indent=2)

    # Visual 2: Severity & CISA KEV breakdown (clusteredColumnChart)
    sev_bar_dir = p1_vis_dir / "v19_bar_severity"
    sev_bar_dir.mkdir(parents=True, exist_ok=True)
    with open(sev_bar_dir / "visual.json", "w", encoding="utf-8") as f:
        json.dump({
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
            "name": "v19_bar_severity",
            "position": {"x": 1325, "y": 660, "z": 700, "height": 390, "width": 560, "tabOrder": 31},
            "visual": {
                "visualType": "clusteredColumnChart",
                "query": {
                    "queryState": {
                        "Category": {
                            "projections": [
                                {
                                    "field": {
                                        "Column": {
                                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
                                            "Property": "Severity"
                                        }
                                    },
                                    "queryRef": "crowdstrike_vulnerability_device_reporting.Severity",
                                    "nativeQueryRef": "Severity",
                                    "active": True
                                }
                            ]
                        },
                        "Series": {
                            "projections": [
                                {
                                    "field": {
                                        "Column": {
                                            "Expression": {"SourceRef": {"Entity": "crowdstrike_vulnerability_device_reporting"}},
                                            "Property": "is_cisa_kev"
                                        }
                                    },
                                    "queryRef": "crowdstrike_vulnerability_device_reporting.is_cisa_kev",
                                    "nativeQueryRef": "is_cisa_kev"
                                }
                            ]
                        },
                        "Y": {
                            "projections": [
                                {
                                    "field": {
                                        "Measure": {
                                            "Expression": {"SourceRef": {"Entity": "_Measures"}},
                                            "Property": "Open Vulnerabilities"
                                        }
                                    },
                                    "queryRef": "_Measures.Open Vulnerabilities",
                                    "nativeQueryRef": "Open Vulnerabilities"
                                }
                            ]
                        }
                    }
                },
                "visualContainerObjects": {
                    "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}],
                    "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                    "title": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "text": {"expr": {"Literal": {"Value": "'Open Vulnerabilities by Severity & CISA KEV (Drillthrough Available)'"}}}, "titleWrap": {"expr": {"Literal": {"Value": "true"}}}}}]
                }
            }
        }, f, indent=2)

    print("  Executive Summary visuals rebalanced to fill space.")

def synchronize_pbix():
    print(f"--- 5. Synchronizing PBIX Archive {PBIX_PATH.name} ---")
    if not PBIX_PATH.exists():
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

def main():
    print("=========================================================")
    print("  Moving Details to Drillthrough Tab & Rebalancing Executive Summary")
    print("=========================================================")
    update_pages_order()
    create_tab3_drillthrough_page()
    setup_tab3_visuals()
    adjust_executive_summary()
    synchronize_pbix()
    print("=========================================================")
    print("  Drillthrough Tab Created & Executive Summary Balanced!")
    print("=========================================================")

if __name__ == "__main__":
    main()
