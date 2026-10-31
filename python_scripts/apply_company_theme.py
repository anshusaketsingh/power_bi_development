#!/usr/bin/env python3
"""
apply_company_theme.py
Applies the James Hardie corporate report theme template (from pbi_report_theme_template)
to the CrowdStrike Windows Vulnerability Dashboard PBIP and synchronizes the PBIX archive.

Actions:
1. Copies RegisteredResources (GreenPalette JSON, JH Logo, jh_without_filter_shelf, Untitled_design)
   and SharedResources (CY24SU10) from pbi_report_theme_template to CS Dashboard.Report.
2. Updates report.json with themeCollection (GreenPalette custom theme, CY24SU10 base theme)
   and resourcePackages referencing RegisteredResources and SharedResources.
3. Updates page.json for both tabs with the corporate branded canvas background (jh_without_filter_shelf).
4. Inserts the James Hardie corporate logo on both tabs within the top header shelf.
5. Updates banner title text to crisp white bold styling on transparent background.
6. Refines slicers with transparent backgrounds to sit seamlessly on the dark green header banner.
7. Styles KPI cards, combo charts, bar charts, and data grids with clean rounded borders and card backgrounds.
8. Synchronizes both Report/definition/ and Report/StaticResources/ into CS Dashboard.pbix.
"""

import os
import shutil
import json
import zipfile
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
TEMPLATE_REP = BASE_DIR / "development" / "pbi_report_theme_template" / "JH Theme.Report"
TARGET_REP = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard" / "CS Dashboard.Report"
PBIX_PATH = BASE_DIR / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"

def copy_static_resources():
    print("--- Copying StaticResources from theme template ---")
    src_registered = TEMPLATE_REP / "StaticResources" / "RegisteredResources"
    dst_registered = TARGET_REP / "StaticResources" / "RegisteredResources"
    dst_registered.mkdir(parents=True, exist_ok=True)
    
    for f in src_registered.iterdir():
        if f.is_file():
            dest_file = dst_registered / f.name
            shutil.copy2(f, dest_file)
            print(f"  Copied {f.name} -> {dest_file.relative_to(BASE_DIR)}")

    src_shared = TEMPLATE_REP / "StaticResources" / "SharedResources" / "BaseThemes"
    dst_shared = TARGET_REP / "StaticResources" / "SharedResources" / "BaseThemes"
    dst_shared.mkdir(parents=True, exist_ok=True)
    
    for f in src_shared.iterdir():
        if f.is_file():
            dest_file = dst_shared / f.name
            shutil.copy2(f, dest_file)
            print(f"  Copied {f.name} -> {dest_file.relative_to(BASE_DIR)}")

def update_report_json():
    print("--- Updating report.json with GreenPalette custom theme and resourcePackages ---")
    rep_json_path = TARGET_REP / "definition" / "report.json"
    with open(rep_json_path, "r", encoding="utf-8") as f:
        rep_def = json.load(f)

    rep_def["themeCollection"] = {
        "baseTheme": {
            "name": "CY24SU10",
            "reportVersionAtImport": {
                "visual": "1.8.98",
                "report": "2.0.98",
                "page": "1.3.98"
            },
            "type": "SharedResources"
        },
        "customTheme": {
            "name": "GreenPalette5172759557985228.json",
            "reportVersionAtImport": {
                "visual": "1.8.98",
                "report": "2.0.98",
                "page": "1.3.98"
            },
            "type": "RegisteredResources"
        }
    }

    rep_def["resourcePackages"] = [
        {
            "name": "RegisteredResources",
            "type": "RegisteredResources",
            "items": [
                {
                    "name": "GreenPalette5172759557985228.json",
                    "path": "GreenPalette5172759557985228.json",
                    "type": "Image"
                },
                {
                    "name": "James_Hardie_Logo20621795536914578.jpg",
                    "path": "James_Hardie_Logo20621795536914578.jpg",
                    "type": "Image"
                },
                {
                    "name": "jh_without_filter_shelf7281792610297229.png",
                    "path": "jh_without_filter_shelf7281792610297229.png",
                    "type": "Image"
                },
                {
                    "name": "Untitled_design844922143885944.png",
                    "path": "Untitled_design844922143885944.png",
                    "type": "Image"
                }
            ]
        },
        {
            "name": "SharedResources",
            "type": "SharedResources",
            "items": [
                {
                    "name": "CY24SU10",
                    "path": "BaseThemes/CY24SU10.json",
                    "type": "BaseTheme"
                }
            ]
        }
    ]

    rep_def["objects"] = {
        "section": [
            {
                "properties": {
                    "verticalAlignment": {
                        "expr": {
                            "Literal": {
                                "Value": "'Top'"
                            }
                        }
                    }
                }
            }
        ],
        "outspacePane": [
            {
                "properties": {
                    "expanded": {
                        "expr": {
                            "Literal": {
                                "Value": "false"
                            }
                        }
                    },
                    "visible": {
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

    with open(rep_json_path, "w", encoding="utf-8") as f:
        json.dump(rep_def, f, indent=2)
    print("  Successfully updated report.json")

def update_page_backgrounds():
    print("--- Updating page backgrounds to corporate branded canvas ---")
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
                                                "Value": "'jh_without_filter_shelf.png'"
                                            }
                                        }
                                    },
                                    "url": {
                                        "expr": {
                                            "ResourcePackageItem": {
                                                "PackageName": "RegisteredResources",
                                                "PackageType": 1,
                                                "ItemName": "jh_without_filter_shelf7281792610297229.png"
                                            }
                                        }
                                    },
                                    "scaling": {
                                        "expr": {
                                            "Literal": {
                                                "Value": "'Fill'"
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

def setup_page1_visuals():
    print("--- Configuring Page 1 visuals with JH Logo, Header, and Card styling ---")
    p1_vis_dir = TARGET_REP / "definition" / "pages" / "47081098f92a957d7fd0" / "visuals"
    
    # 1. James Hardie Logo visual
    logo_dir = p1_vis_dir / "v00_logo_jh0000000"
    logo_dir.mkdir(parents=True, exist_ok=True)
    logo_def = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v00_logo_jh0000000",
        "position": {
            "x": 30,
            "y": 18,
            "z": 50,
            "height": 62,
            "width": 160,
            "tabOrder": 0
        },
        "visual": {
            "visualType": "image",
            "objects": {
                "general": [
                    {
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
                    }
                ],
                "imageScaling": [
                    {
                        "properties": {
                            "imageScalingType": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'Fit'"
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
    with open(logo_dir / "visual.json", "w", encoding="utf-8") as f:
        json.dump(logo_def, f, indent=2)

    # 2. Title Textbox (sitting next to logo)
    title_dir = p1_vis_dir / "v01_banner_title000"
    title_def = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "v01_banner_title000",
        "position": {
            "x": 205,
            "y": 18,
            "z": 100,
            "height": 62,
            "width": 690,
            "tabOrder": 1
        },
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
                                            "value": "CrowdStrike Windows Vulnerability & Patch Compliance",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "19pt",
                                                "fontWeight": "bold",
                                                "color": {
                                                    "solid": {
                                                        "color": "#FFFFFF"
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "value": "\nExecutive Board Reporting | Scope: Microsoft Windows Only",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "10pt",
                                                "fontWeight": "normal",
                                                "color": {
                                                    "solid": {
                                                        "color": "#C6E2D1"
                                                    }
                                                }
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
    with open(title_dir / "visual.json", "w", encoding="utf-8") as f:
        json.dump(title_def, f, indent=2)

    # 3. Slicers: transparent background to blend into dark green banner
    slicer_configs = [
        ("v02_slicer_platform0", 905, 18, 225, 62),
        ("v03_slicer_vendor000", 1140, 18, 225, 62),
        ("v04_slicer_weekstart", 1375, 18, 250, 62),
        ("v13_slicer_sla_thresh", 1635, 18, 255, 62),
    ]
    for sname, x, y, w, h in slicer_configs:
        spath = p1_vis_dir / sname / "visual.json"
        if spath.exists():
            with open(spath, "r", encoding="utf-8") as f:
                sdef = json.load(f)
            sdef["position"]["x"] = x
            sdef["position"]["y"] = y
            sdef["position"]["width"] = w
            sdef["position"]["height"] = h
            sdef.setdefault("visual", {})["visualContainerObjects"] = {
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
            with open(spath, "w", encoding="utf-8") as f:
                json.dump(sdef, f, indent=2)

    # 4. KPI Cards, Charts, and Grid: rounded card borders and clean card background
    card_and_chart_configs = [
        # (name, x, y, w, h)
        ("v05_kpi_openvulns00", 30, 105, 296, 130),
        ("v07_kpi_cisakev0000", 342, 105, 296, 130),
        ("v06_kpi_openover30d", 654, 105, 296, 130),
        ("v08_kpi_patchrate00", 966, 105, 296, 130),
        ("v14_kpi_reboot30d", 1278, 105, 296, 130),
        ("v09_kpi_devexcept00", 1590, 105, 296, 130),
        ("v10_trend_combo0000", 30, 255, 1150, 415),
        ("v11_aging_barchart0", 1200, 255, 690, 415),
        ("v12_detail_grid0000", 30, 690, 1860, 365),
    ]
    for vname, x, y, w, h in card_and_chart_configs:
        vpath = p1_vis_dir / vname / "visual.json"
        if vpath.exists():
            with open(vpath, "r", encoding="utf-8") as f:
                vdef = json.load(f)
            vdef["position"]["x"] = x
            vdef["position"]["y"] = y
            vdef["position"]["width"] = w
            vdef["position"]["height"] = h
            vdef.setdefault("visual", {})["visualContainerObjects"] = {
                "border": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "radius": {
                                "expr": {
                                    "Literal": {
                                        "Value": "8D"
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
                                        "Value": "true"
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
            with open(vpath, "w", encoding="utf-8") as f:
                json.dump(vdef, f, indent=2)
    print("  Page 1 visuals successfully updated.")

def setup_page2_visuals():
    print("--- Configuring Page 2 visuals with JH Logo, Header, and Card styling ---")
    p2_vis_dir = TARGET_REP / "definition" / "pages" / "p02_trends_exceptions" / "visuals"
    
    # 1. James Hardie Logo visual
    logo_dir = p2_vis_dir / "p2_v00_logo_jh00000"
    logo_dir.mkdir(parents=True, exist_ok=True)
    logo_def = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p2_v00_logo_jh00000",
        "position": {
            "x": 30,
            "y": 18,
            "z": 50,
            "height": 62,
            "width": 160,
            "tabOrder": 0
        },
        "visual": {
            "visualType": "image",
            "objects": {
                "general": [
                    {
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
                    }
                ],
                "imageScaling": [
                    {
                        "properties": {
                            "imageScalingType": {
                                "expr": {
                                    "Literal": {
                                        "Value": "'Fit'"
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
    with open(logo_dir / "visual.json", "w", encoding="utf-8") as f:
        json.dump(logo_def, f, indent=2)

    # 2. Title Textbox (sitting next to logo)
    title_dir = p2_vis_dir / "p2_v01_banner_title"
    title_def = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": "p2_v01_banner_title",
        "position": {
            "x": 205,
            "y": 18,
            "z": 100,
            "height": 62,
            "width": 880,
            "tabOrder": 1
        },
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
                                            "value": "CrowdStrike Trends & Device Exceptions",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "19pt",
                                                "fontWeight": "bold",
                                                "color": {
                                                    "solid": {
                                                        "color": "#FFFFFF"
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            "value": "\nRemediation Rate Trends, Severity Breakdown & Device Patch Exceptions",
                                            "textStyle": {
                                                "fontFamily": "Segoe UI",
                                                "fontSize": "10pt",
                                                "fontWeight": "normal",
                                                "color": {
                                                    "solid": {
                                                        "color": "#C6E2D1"
                                                    }
                                                }
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
    with open(title_dir / "visual.json", "w", encoding="utf-8") as f:
        json.dump(title_def, f, indent=2)

    # 3. Slicers: transparent background
    slicer_configs = [
        ("p2_v02_slicer_week", 1100, 18, 250, 62),
        ("p2_v03_slicer_severity", 1365, 18, 255, 62),
        ("p2_v04_slicer_exception", 1635, 18, 255, 62),
    ]
    for sname, x, y, w, h in slicer_configs:
        spath = p2_vis_dir / sname / "visual.json"
        if spath.exists():
            with open(spath, "r", encoding="utf-8") as f:
                sdef = json.load(f)
            sdef["position"]["x"] = x
            sdef["position"]["y"] = y
            sdef["position"]["width"] = w
            sdef["position"]["height"] = h
            sdef.setdefault("visual", {})["visualContainerObjects"] = {
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
            with open(spath, "w", encoding="utf-8") as f:
                json.dump(sdef, f, indent=2)

    # 4. Deep-dive visuals & grid
    charts_and_grid = [
        ("p2_v05_trend_remed_rate", 30, 105, 600, 435),
        ("p2_v06_bar_severity_kev", 650, 105, 600, 435),
        ("p2_v07_bar_device_exceptions", 1270, 105, 620, 435),
        ("p2_v08_grid_investigation", 30, 560, 1860, 495),
    ]
    for vname, x, y, w, h in charts_and_grid:
        vpath = p2_vis_dir / vname / "visual.json"
        if vpath.exists():
            with open(vpath, "r", encoding="utf-8") as f:
                vdef = json.load(f)
            vdef["position"]["x"] = x
            vdef["position"]["y"] = y
            vdef["position"]["width"] = w
            vdef["position"]["height"] = h
            vdef.setdefault("visual", {})["visualContainerObjects"] = {
                "border": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "radius": {
                                "expr": {
                                    "Literal": {
                                        "Value": "8D"
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
                                        "Value": "true"
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
            with open(vpath, "w", encoding="utf-8") as f:
                json.dump(vdef, f, indent=2)
    print("  Page 2 visuals successfully updated.")

def synchronize_pbix():
    print(f"--- Synchronizing PBIX Archive {PBIX_PATH.name} ---")
    if not PBIX_PATH.exists():
        print("  PBIX file does not exist, skipping PBIX sync.")
        return

    temp_pbix = PBIX_PATH.with_suffix(".tmp.pbix")
    
    # Collect all definition files
    new_report_files = {}
    for root, _, files in os.walk(TARGET_REP / "definition"):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(TARGET_REP / "definition")
            archive_path = f"Report/definition/{rel_path.as_posix()}"
            with open(full_path, "rb") as fh:
                new_report_files[archive_path] = fh.read()

    # Collect all StaticResources files
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
    print("  Applying Corporate Theme Template to CrowdStrike Dashboard")
    print("=========================================================")
    copy_static_resources()
    update_report_json()
    update_page_backgrounds()
    setup_page1_visuals()
    setup_page2_visuals()
    synchronize_pbix()
    print("=========================================================")
    print("  Company Theme Applied Successfully!")
    print("=========================================================")

if __name__ == "__main__":
    main()
