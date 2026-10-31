#!/usr/bin/env python3
"""
update_dynamic_sla_free_entry.py

Configures the SLA Threshold slicer across the Power BI report as a free-entry numeric field
in 'After' mode (>= threshold), allowing users to type any random day count (e.g. 700, 45, 120),
and synchronizes this filter across all report visuals, KPIs, and data grids.
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

def update_sla_slicer():
    print("--- 1. Updating Executive Summary SLA Slicer (v13_slicer_sla_thresh) ---")
    slicer_dir = TARGET_REP / "definition" / "pages" / "47081098f92a957d7fd0" / "visuals" / "v13_slicer_sla_thresh"
    slicer_path = slicer_dir / "visual.json"
    
    with open(slicer_path, "r", encoding="utf-8") as f:
        sdata = json.load(f)
    
    # 1. Set mode to 'After' (Greater than or equal to - free numeric entry box)
    sdata["visual"]["objects"]["data"] = [
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
    ]
    
    # Ensure slider is shown and styled
    sdata["visual"]["objects"]["slider"] = [
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
    ]
    
    # Set syncGroup so filter changes propagate across tabs
    sdata["visual"]["syncGroup"] = {
        "groupName": "SLA Threshold",
        "fieldChanges": True,
        "filterChanges": True
    }
    
    with open(slicer_path, "w", encoding="utf-8") as f:
        json.dump(sdata, f, indent=2)
    print("  v13_slicer_sla_thresh configured with mode 'After' and syncGroup 'SLA Threshold'.")
    return sdata

def add_synced_slicer_to_tab2(base_slicer_data):
    print("--- 2. Adding Synced SLA Slicer to Tab 2 (p02_trends_exceptions) ---")
    p2_dir = TARGET_REP / "definition" / "pages" / "p02_trends_exceptions" / "visuals" / "p2_v13_slicer_sla_thresh"
    p2_dir.mkdir(parents=True, exist_ok=True)
    p2_path = p2_dir / "visual.json"
    
    p2_data = json.loads(json.dumps(base_slicer_data))
    p2_data["name"] = "p2_v13_slicer_sla_thresh"
    p2_data["position"] = {
        "x": 28,
        "y": 617,
        "z": 12000,
        "height": 72,
        "width": 275,
        "tabOrder": 12000
    }
    with open(p2_path, "w", encoding="utf-8") as f:
        json.dump(p2_data, f, indent=2)
    print("  p2_v13_slicer_sla_thresh created on Tab 2 at y=617.")

def add_synced_slicer_to_tab3(base_slicer_data):
    print("--- 3. Adding Synced SLA Slicer to Tab 3 (p03_vulnerability_details) ---")
    p3_dir = TARGET_REP / "definition" / "pages" / "p03_vulnerability_details" / "visuals" / "p3_v13_slicer_sla_thresh"
    p3_dir.mkdir(parents=True, exist_ok=True)
    p3_path = p3_dir / "visual.json"
    
    p3_data = json.loads(json.dumps(base_slicer_data))
    p3_data["name"] = "p3_v13_slicer_sla_thresh"
    p3_data["position"] = {
        "x": 28,
        "y": 535,
        "z": 12000,
        "height": 72,
        "width": 275,
        "tabOrder": 12000
    }
    with open(p3_path, "w", encoding="utf-8") as f:
        json.dump(p3_data, f, indent=2)
    print("  p3_v13_slicer_sla_thresh created on Tab 3 at y=535.")

def update_detail_grid_filtering():
    print("--- 4. Updating Granular Detail Grid (p3_v02_detail_grid) ---")
    grid_path = TARGET_REP / "definition" / "pages" / "p03_vulnerability_details" / "visuals" / "p3_v02_detail_grid" / "visual.json"
    with open(grid_path, "r", encoding="utf-8") as f:
        gdata = json.load(f)
    
    # In projections, replace "Selected SLA Days" with "Open Vulnerabilities"
    projections = gdata["visual"]["query"]["queryState"]["Values"]["projections"]
    new_projections = []
    for proj in projections:
        prop = proj.get("field", {}).get("Measure", {}).get("Property")
        if prop == "Selected SLA Days":
            new_projections.append({
                "field": {
                    "Measure": {
                        "Expression": {
                            "SourceRef": {
                                "Entity": "_Measures"
                            }
                        },
                        "Property": "Open Vulnerabilities"
                    }
                },
                "queryRef": "_Measures.Open Vulnerabilities",
                "nativeQueryRef": "Open Vulnerabilities"
            })
        else:
            new_projections.append(proj)
    gdata["visual"]["query"]["queryState"]["Values"]["projections"] = new_projections
    
    # In filterConfig, ensure filter on Open Vulnerabilities is present so only rows matching SLA cutoff are shown
    filters = gdata.get("filterConfig", {}).get("filters", [])
    new_filters = []
    for flt in filters:
        prop = flt.get("field", {}).get("Measure", {}).get("Property")
        if prop == "Selected SLA Days":
            continue
        new_filters.append(flt)
    
    # Add filter on Open Vulnerabilities > 0
    has_open_vuln_filter = any(flt.get("field", {}).get("Measure", {}).get("Property") == "Open Vulnerabilities" for flt in new_filters)
    if not has_open_vuln_filter:
        new_filters.append({
            "name": "FilterOpenVulnsOnly",
            "field": {
                "Measure": {
                    "Expression": {
                        "SourceRef": {
                            "Entity": "_Measures"
                        }
                    },
                    "Property": "Open Vulnerabilities"
                }
            },
            "type": "Advanced",
            "filter": {
                "Version": 2,
                "From": [
                    {
                        "Name": "m",
                        "Entity": "_Measures",
                        "Type": 0
                    }
                ],
                "Where": [
                    {
                        "Condition": {
                            "Comparison": {
                                "ComparisonKind": 1,
                                "Left": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Source": "m"
                                            }
                                        },
                                        "Property": "Open Vulnerabilities"
                                    }
                                },
                                "Right": {
                                    "Literal": {
                                        "Value": "0D"
                                    }
                                }
                            }
                        }
                    }
                ]
            },
            "howCreated": "User"
        })
    
    gdata["filterConfig"] = {"filters": new_filters}
    
    with open(grid_path, "w", encoding="utf-8") as f:
        json.dump(gdata, f, indent=2)
    print("  p3_v02_detail_grid updated with Open Vulnerabilities projection and > 0 filter.")

def update_investigation_grid_filtering():
    print("--- 5. Updating Tab 2 Investigation Grid (p2_v08_grid_investigation) ---")
    grid_path = TARGET_REP / "definition" / "pages" / "p02_trends_exceptions" / "visuals" / "p2_v08_grid_investigation" / "visual.json"
    with open(grid_path, "r", encoding="utf-8") as f:
        gdata = json.load(f)
    
    gdata["filterConfig"] = {
        "filters": [
            {
                "name": "FilterOpenVulnsOnlyP2",
                "field": {
                    "Measure": {
                        "Expression": {
                            "SourceRef": {
                                "Entity": "_Measures"
                            }
                        },
                        "Property": "Open Vulnerabilities"
                    }
                },
                "type": "Advanced",
                "filter": {
                    "Version": 2,
                    "From": [
                        {
                            "Name": "m",
                            "Entity": "_Measures",
                            "Type": 0
                        }
                    ],
                    "Where": [
                        {
                            "Condition": {
                                "Comparison": {
                                    "ComparisonKind": 1,
                                    "Left": {
                                        "Measure": {
                                            "Expression": {
                                                "SourceRef": {
                                                    "Source": "m"
                                                }
                                            },
                                            "Property": "Open Vulnerabilities"
                                        }
                                    },
                                    "Right": {
                                        "Literal": {
                                            "Value": "0D"
                                        }
                                    }
                                }
                            }
                        }
                    ]
                },
                "howCreated": "User"
            }
        ]
    }
    
    with open(grid_path, "w", encoding="utf-8") as f:
        json.dump(gdata, f, indent=2)
    print("  p2_v08_grid_investigation updated with Open Vulnerabilities > 0 filter.")

def sync_pbix():
    print(f"--- 6. Synchronizing PBIX Archive {PBIX_PATH.name} ---")
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
    base_slicer = update_sla_slicer()
    add_synced_slicer_to_tab2(base_slicer)
    add_synced_slicer_to_tab3(base_slicer)
    update_detail_grid_filtering()
    update_investigation_grid_filtering()
    sync_pbix()
    print("--- ALL UPDATES COMPLETED SUCCESSFULLY ---")
