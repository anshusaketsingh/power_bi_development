#!/usr/bin/env python3
"""
apply_left_filter_pane_template.py
Applies the James Hardie "Standard Design - With Filter" company template
(using Untitled_design844922143885944.png with dedicated left vertical filter pane).

Features:
- Page background: Untitled_design844922143885944.png (green header banner + left vertical filter shelf)
- Top-left: James Hardie corporate logo (above left filter pane)
- Top banner: Executive title & subtitle in bold white text (#FFFFFF, #C6E2D1) on transparent background
- Left filter shelf: Stacked slicers with white bold headers, dropdown mode, and "Clear All Slicers" button
- Right content area: 
    * Tab 1: 6 KPI cards in executive card row, 2 charts in middle row, operational detail grid at bottom
    * Tab 2: 3 deep-dive trend/breakdown charts in top row, device exception investigation grid at bottom
- Full synchronization into CS Dashboard.pbix
"""

import os
import shutil
import json
import zipfile
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
TARGET_REP = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard" / "CS Dashboard.Report"
PBIX_PATH = BASE_DIR / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"

def update_page_backgrounds():
    print("--- 1. Setting page backgrounds to 'Untitled_design844922143885944.png' (Standard Design - With Filter) ---")
    pages = [
        ("47081098f92a957d7fd0", "Executive Summary"),
        ("p02_trends_exceptions", "Trends & Device Exceptions")
    ]
    for page_id, display_name in pages:
        page_path = TARGET_REP / "definition" / "pages" / page_id / "page.json"
        page_def = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": page_id,
            "displayName": display_name,
            "displayOption": "FitToPage",
            "height": 1080,
            "width": 1920,
            "objects": {
                "background": [
                    {
                        "properties": {
                            "image": {
                                "image": {
                                    "name": {
                                        "expr": {
                                            "Literal": {
                                                "Value": "'Untitled design.png'"
                                            }
                                        }
                                    },
                                    "url": {
                                        "expr": {
                                            "ResourcePackageItem": {
                                                "PackageName": "RegisteredResources",
                                                "PackageType": 1,
                                                "ItemName": "Untitled_design844922143885944.png"
                                            }
                                        }
                                    },
                                    "scaling": {
                                        "expr": {
                                            "Literal": {
                                                "Value": "'Fit'"
                                            }
                                        }
                                    }
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
                            "transparency": {
                                "expr": {
                                    "Literal": {
                                        "Value": "0D"
                                    }
                                }
                            }
                        }
                    }
                ]
            }
        }
        with open(page_path, "w", encoding="utf-8") as f:
            json.dump(page_def, f, indent=2)
        print(f"  Configured background for {display_name} ({page_id})")

def make_slicer_def(vname, x, y, w, h, table_name, col_name, z=200, tab_order=2):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": vname,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "height": h,
            "width": w,
            "tabOrder": tab_order
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
                                                "Entity": table_name
                                            }
                                        },
                                        "Property": col_name
                                    }
                                },
                                "queryRef": f"{table_name}.{col_name}",
                                "nativeQueryRef": col_name
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
                                        "Value": "'Dropdown'"
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
            }
        }
    }

def make_clear_button_def(vname, x, y, w, h, z=6000, tab_order=90):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": vname,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "height": h,
            "width": w,
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "actionButton",
            "objects": {
                "icon": [
                    {
                        "properties": {
                            "shapeType": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'clearAllSlicers'"
                                    }
                                }
                            }
                        },
                        "selector": {
                            "id": "default"
                        }
                    },
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "lineColor": {
                                "solid": {
                                    "color": {
                                        "expr": {
                                            "Literal": {
                                                "Value": "'#1b4332'"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                ],
                "text": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            }
                        }
                    },
                    {
                        "properties": {
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'Clear All Slicers'"
                                    }
                                }
                            },
                            "horizontalAlignment": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'center'"
                                    }
                                }
                            },
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
                            "bold": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "fontSize": {
                                "expr": {
                                    "Literal": {
                                        "Value": "10D"
                                    }
                                }
                            }
                        },
                        "selector": {
                            "id": "default"
                        }
                    }
                ],
                "shape": [
                    {
                        "properties": {
                            "roundEdge": {
                                "expr": {
                                    "Literal": {
                                        "Value": "18L"
                                    }
                                }
                            }
                        },
                        "selector": {
                            "id": "default"
                        }
                    }
                ],
                "fill": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "fillColor": {
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
                        },
                        "selector": {
                            "id": "default"
                        }
                    }
                ]
            },
            "visualContainerObjects": {
                "visualLink": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "type": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'ClearAllSlicers'"
                                    }
                                }
                            },
                            "tooltipPlaceholderText": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'Clear all slicers on this page'"
                                    }
                                }
                            }
                        }
                    }
                ],
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
            "drillFilterOtherVisuals": True
        },
        "howCreated": "InsertVisualButton"
    }

def setup_page1_left_filter_layout():
    print("--- 2. Setting up Page 1 (Executive Summary) with Left Filter Pane ---")
    p1_vis_dir = TARGET_REP / "definition" / "pages" / "47081098f92a957d7fd0" / "visuals"

    # Logo (top-left above filter pane): x=35, y=18, w=260, h=80
    logo_path = p1_vis_dir / "v00_logo_jh0000000" / "visual.json"
    with open(logo_path, "r", encoding="utf-8") as f:
        logo_def = json.load(f)
    logo_def["position"] = {"x": 35, "y": 18, "z": 50, "height": 80, "width": 260, "tabOrder": 0}
    with open(logo_path, "w", encoding="utf-8") as f:
        json.dump(logo_def, f, indent=2)

    # Title in top header banner (spanning right of logo): x=345, y=20, w=1540, h=80
    title_path = p1_vis_dir / "v01_banner_title000" / "visual.json"
    with open(title_path, "r", encoding="utf-8") as f:
        title_def = json.load(f)
    title_def["position"] = {"x": 345, "y": 20, "z": 100, "height": 80, "width": 1540, "tabOrder": 1}
    title_def["visual"]["objects"]["general"][0]["properties"]["paragraphs"][0]["textRuns"] = [
        {
            "value": "CrowdStrike Windows Vulnerability & Patch Compliance",
            "textStyle": {
                "fontFamily": "Segoe UI",
                "fontSize": "21pt",
                "fontWeight": "bold",
                "color": {"solid": {"color": "#FFFFFF"}}
            }
        },
        {
            "value": "\nExecutive Board Reporting | Scope: Microsoft Windows Only",
            "textStyle": {
                "fontFamily": "Segoe UI",
                "fontSize": "11pt",
                "fontWeight": "normal",
                "color": {"solid": {"color": "#C6E2D1"}}
            }
        }
    ]
    with open(title_path, "w", encoding="utf-8") as f:
        json.dump(title_def, f, indent=2)

    # Stacked Slicers on Left Filter Pane (x=28, w=275, h=72, gap=10)
    # y coordinates: 125, 207, 289, 371, 453, 535, 617
    slicers_info = [
        ("v02_slicer_platform0", 125, "crowdstrike_vulnerability_device_reporting", "Platform", 2),
        ("v03_slicer_vendor000", 207, "crowdstrike_vulnerability_device_reporting", "Vendor Normalized", 3),
        ("v04_slicer_weekstart", 289, "Calendar", "Week Start", 4),
        ("v13_slicer_sla_thresh", 371, "SLA Threshold", "Threshold Label", 5),
    ]
    for vname, y, table_name, col_name, to in slicers_info:
        sdir = p1_vis_dir / vname
        sdir.mkdir(parents=True, exist_ok=True)
        sdef = make_slicer_def(vname, x=28, y=y, w=275, h=72, table_name=table_name, col_name=col_name, z=200+to, tab_order=to)
        with open(sdir / "visual.json", "w", encoding="utf-8") as f:
            json.dump(sdef, f, indent=2)

    # Additional left-pane slicers: Severity & CISA KEV & Exception
    extra_slicers = [
        ("v15_slicer_severity", 453, "crowdstrike_vulnerability_device_reporting", "Severity", 6),
        ("v16_slicer_cisakev", 535, "crowdstrike_vulnerability_device_reporting", "is_cisa_kev", 7),
        ("v17_slicer_devexcept", 617, "crowdstrike_vulnerability_device_reporting", "Device Patch Exception", 8),
    ]
    for vname, y, table_name, col_name, to in extra_slicers:
        sdir = p1_vis_dir / vname
        sdir.mkdir(parents=True, exist_ok=True)
        sdef = make_slicer_def(vname, x=28, y=y, w=275, h=72, table_name=table_name, col_name=col_name, z=200+to, tab_order=to)
        with open(sdir / "visual.json", "w", encoding="utf-8") as f:
            json.dump(sdef, f, indent=2)

    # Clear All Slicers button at bottom of left filter pane: x=55, y=980, w=220, h=38
    btn_dir = p1_vis_dir / "v_btn_clear_slicers"
    btn_dir.mkdir(parents=True, exist_ok=True)
    btn_def = make_clear_button_def("v_btn_clear_slicers", x=55, y=980, w=220, h=38, z=6000, tab_order=90)
    with open(btn_dir / "visual.json", "w", encoding="utf-8") as f:
        json.dump(btn_def, f, indent=2)

    # Content Canvas Area (x=345 to x=1885 -> 1540px wide)
    # Row 1: 6 KPI Cards (y=125, h=115, w=244 each, gap=15)
    # Total span: 6 * 244 + 5 * 15 = 1464 + 75 = 1539px
    kpis = [
        ("v05_kpi_openvulns00", 345),
        ("v07_kpi_cisakev0000", 604),
        ("v06_kpi_openover30d", 863),
        ("v08_kpi_patchrate00", 1122),
        ("v14_kpi_reboot30d", 1381),
        ("v09_kpi_devexcept00", 1640),
    ]
    for vname, x in kpis:
        kpath = p1_vis_dir / vname / "visual.json"
        if kpath.exists():
            with open(kpath, "r", encoding="utf-8") as f:
                kdef = json.load(f)
            kdef["position"] = {"x": x, "y": 125, "z": 500, "height": 115, "width": 244, "tabOrder": 10}
            kdef.setdefault("visual", {})["visualContainerObjects"] = {
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}]
            }
            with open(kpath, "w", encoding="utf-8") as f:
                json.dump(kdef, f, indent=2)

    # Row 2: Charts (y=255, h=405)
    # Combo chart: x=345, w=955; Aging Bar chart: x=1315, w=570
    combo_path = p1_vis_dir / "v10_trend_combo0000" / "visual.json"
    if combo_path.exists():
        with open(combo_path, "r", encoding="utf-8") as f:
            cdef = json.load(f)
        cdef["position"] = {"x": 345, "y": 255, "z": 700, "height": 405, "width": 955, "tabOrder": 20}
        cdef.setdefault("visual", {})["visualContainerObjects"] = {
            "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}],
            "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
            "title": [{"properties": {"titleWrap": {"expr": {"Literal": {"Value": "true"}}}}}]
        }
        with open(combo_path, "w", encoding="utf-8") as f:
            json.dump(cdef, f, indent=2)

    aging_path = p1_vis_dir / "v11_aging_barchart0" / "visual.json"
    if aging_path.exists():
        with open(aging_path, "r", encoding="utf-8") as f:
            adef = json.load(f)
        adef["position"] = {"x": 1315, "y": 255, "z": 700, "height": 405, "width": 570, "tabOrder": 21}
        adef.setdefault("visual", {})["visualContainerObjects"] = {
            "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}],
            "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
            "title": [{"properties": {"titleWrap": {"expr": {"Literal": {"Value": "true"}}}}}]
        }
        with open(aging_path, "w", encoding="utf-8") as f:
            json.dump(adef, f, indent=2)

    # Row 3: Operational Detail Grid (y=675, h=375, w=1540, x=345)
    grid_path = p1_vis_dir / "v12_detail_grid0000" / "visual.json"
    if grid_path.exists():
        with open(grid_path, "r", encoding="utf-8") as f:
            gdef = json.load(f)
        gdef["position"] = {"x": 345, "y": 675, "z": 800, "height": 375, "width": 1540, "tabOrder": 30}
        gdef.setdefault("visual", {})["visualContainerObjects"] = {
            "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}],
            "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
            "title": [{"properties": {"titleWrap": {"expr": {"Literal": {"Value": "true"}}}}}]
        }
        with open(grid_path, "w", encoding="utf-8") as f:
            json.dump(gdef, f, indent=2)

    print("  Page 1 (Executive Summary) configured with left-side filter pane.")

def setup_page2_left_filter_layout():
    print("--- 3. Setting up Page 2 (Trends & Device Exceptions) with Left Filter Pane ---")
    p2_vis_dir = TARGET_REP / "definition" / "pages" / "p02_trends_exceptions" / "visuals"

    # Logo: x=35, y=18, w=260, h=80
    logo_path = p2_vis_dir / "p2_v00_logo_jh00000" / "visual.json"
    with open(logo_path, "r", encoding="utf-8") as f:
        logo_def = json.load(f)
    logo_def["position"] = {"x": 35, "y": 18, "z": 50, "height": 80, "width": 260, "tabOrder": 0}
    with open(logo_path, "w", encoding="utf-8") as f:
        json.dump(logo_def, f, indent=2)

    # Title: x=345, y=20, w=1540, h=80
    title_path = p2_vis_dir / "p2_v01_banner_title" / "visual.json"
    with open(title_path, "r", encoding="utf-8") as f:
        title_def = json.load(f)
    title_def["position"] = {"x": 345, "y": 20, "z": 100, "height": 80, "width": 1540, "tabOrder": 1}
    title_def["visual"]["objects"]["general"][0]["properties"]["paragraphs"][0]["textRuns"] = [
        {
            "value": "CrowdStrike Trends & Device Exceptions",
            "textStyle": {
                "fontFamily": "Segoe UI",
                "fontSize": "21pt",
                "fontWeight": "bold",
                "color": {"solid": {"color": "#FFFFFF"}}
            }
        },
        {
            "value": "\nRemediation Rate Trends, Severity Breakdown & Device Patch Exceptions",
            "textStyle": {
                "fontFamily": "Segoe UI",
                "fontSize": "11pt",
                "fontWeight": "normal",
                "color": {"solid": {"color": "#C6E2D1"}}
            }
        }
    ]
    with open(title_path, "w", encoding="utf-8") as f:
        json.dump(title_def, f, indent=2)

    # Left Pane Slicers:
    p2_slicers = [
        ("p2_v02_slicer_week", 125, "Calendar", "Week Start", 2),
        ("p2_v03_slicer_severity", 207, "crowdstrike_vulnerability_device_reporting", "Severity", 3),
        ("p2_v04_slicer_exception", 289, "crowdstrike_vulnerability_device_reporting", "Device Patch Exception", 4),
        ("p2_v10_slicer_platform", 371, "crowdstrike_vulnerability_device_reporting", "Platform", 5),
        ("p2_v11_slicer_cisakev", 453, "crowdstrike_vulnerability_device_reporting", "is_cisa_kev", 6),
        ("p2_v12_slicer_vendor", 535, "crowdstrike_vulnerability_device_reporting", "Vendor Normalized", 7),
    ]
    for vname, y, table_name, col_name, to in p2_slicers:
        sdir = p2_vis_dir / vname
        sdir.mkdir(parents=True, exist_ok=True)
        sdef = make_slicer_def(vname, x=28, y=y, w=275, h=72, table_name=table_name, col_name=col_name, z=200+to, tab_order=to)
        with open(sdir / "visual.json", "w", encoding="utf-8") as f:
            json.dump(sdef, f, indent=2)

    # Clear All Slicers button on Tab 2
    btn_dir = p2_vis_dir / "p2_btn_clear_slicers"
    btn_dir.mkdir(parents=True, exist_ok=True)
    btn_def = make_clear_button_def("p2_btn_clear_slicers", x=55, y=980, w=220, h=38, z=6000, tab_order=90)
    with open(btn_dir / "visual.json", "w", encoding="utf-8") as f:
        json.dump(btn_def, f, indent=2)

    # Content Canvas Area (x=345 to x=1885 -> 1540px wide)
    # Row 1: Deep-dive charts (y=125, h=445)
    # 3 visuals: w=500 each, gap=20 -> 3*500 + 40 = 1540px!
    charts = [
        ("p2_v05_trend_remed_rate", 345, 500, 445),
        ("p2_v06_bar_severity_kev", 865, 500, 445),
        ("p2_v07_bar_device_exceptions", 1385, 500, 445),
    ]
    for vname, x, w, h in charts:
        cpath = p2_vis_dir / vname / "visual.json"
        if cpath.exists():
            with open(cpath, "r", encoding="utf-8") as f:
                cdef = json.load(f)
            cdef["position"] = {"x": x, "y": 125, "z": 700, "height": h, "width": w, "tabOrder": 20}
            cdef.setdefault("visual", {})["visualContainerObjects"] = {
                "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}],
                "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
                "title": [{"properties": {"titleWrap": {"expr": {"Literal": {"Value": "true"}}}}}]
            }
            with open(cpath, "w", encoding="utf-8") as f:
                json.dump(cdef, f, indent=2)

    # Row 2: Investigation Grid (y=585, h=465, w=1540, x=345)
    inv_path = p2_vis_dir / "p2_v08_grid_investigation" / "visual.json"
    if inv_path.exists():
        with open(inv_path, "r", encoding="utf-8") as f:
            idef = json.load(f)
        idef["position"] = {"x": 345, "y": 585, "z": 800, "height": 465, "width": 1540, "tabOrder": 30}
        idef.setdefault("visual", {})["visualContainerObjects"] = {
            "border": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "radius": {"expr": {"Literal": {"Value": "8D"}}}}}],
            "background": [{"properties": {"show": {"expr": {"Literal": {"Value": "true"}}}, "transparency": {"expr": {"Literal": {"Value": "0D"}}}}}],
            "title": [{"properties": {"titleWrap": {"expr": {"Literal": {"Value": "true"}}}}}]
        }
        with open(inv_path, "w", encoding="utf-8") as f:
            json.dump(idef, f, indent=2)

    print("  Page 2 (Trends & Device Exceptions) configured with left-side filter pane.")

def synchronize_pbix():
    print(f"--- 4. Synchronizing PBIX Archive {PBIX_PATH.name} ---")
    if not PBIX_PATH.exists():
        print("  PBIX file does not exist, skipping PBIX sync.")
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
    print("  Applying Left-Side Filter Pane Template Layout")
    print("=========================================================")
    update_page_backgrounds()
    setup_page1_left_filter_layout()
    setup_page2_left_filter_layout()
    synchronize_pbix()
    print("=========================================================")
    print("  Left-Side Filter Pane Template Applied Successfully!")
    print("=========================================================")

if __name__ == "__main__":
    main()
