"""
set_sla_slicer_single_select.py

Enforces Single-Select mode across all SLA Threshold slicers:
- Hides the "Select all" checkbox (selectAllCheckboxEnabled: false)
- Enables strict single selection (singleSelect: true)
- Pre-selects "N/A" by default
- Syncs selection across all tabs in group "SLA Threshold"
"""

import json
import shutil
import time
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
REPORT_PAGES = PROJ / "CS Dashboard.Report" / "definition" / "pages"

VISUAL_PATHS = [
    REPORT_PAGES / "47081098f92a957d7fd0" / "visuals" / "v13_slicer_sla_thresh" / "visual.json",
    REPORT_PAGES / "p02_trends_exceptions" / "visuals" / "p2_v13_slicer_sla_thresh" / "visual.json",
    REPORT_PAGES / "p03_vulnerability_details" / "visuals" / "p3_v13_slicer_sla_thresh" / "visual.json",
    REPORT_PAGES / "p05_vulnerability_details" / "visuals" / "p5_v13_slicer_sla_thresh" / "visual.json"
]

VISUAL_SCHEMA = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"
DARK_GREEN = "#1b4332"

def lit(v):
    return {"expr": {"Literal": {"Value": v}}}

def color(hex_):
    return {"solid": {"color": lit(f"'{hex_}'")}}

def backup():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BASE_DIR / "development" / "jh_crowd_strike" / "backups" / f"pre_single_select_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    for vp in VISUAL_PATHS:
        if vp.exists():
            (dest / vp.parent.name).mkdir(parents=True, exist_ok=True)
            shutil.copy2(vp, dest / vp.parent.name / "visual.json")
    print(f"Pre-flight backup saved at: {dest}")

def apply_single_select():
    print("--- Enabling Single-Select on SLA Threshold Slicers ---")
    
    for vp in VISUAL_PATHS:
        if not vp.exists():
            print(f"  ! Missing file: {vp}")
            continue
            
        v_name = vp.parent.name
        
        # Determine appropriate Y position depending on tab
        if "p05" in str(vp) or "p02" in str(vp):
            y_pos = 617
        elif "p03" in str(vp):
            y_pos = 535
        else:
            y_pos = 371
            
        data = {
            "$schema": VISUAL_SCHEMA,
            "name": v_name,
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
                                "mode": lit("'Dropdown'")
                            }
                        }
                    ],
                    "header": [
                        {
                            "properties": {
                                "show": lit("true"),
                                "text": lit("'SLA Threshold'"),
                                "fontColor": color("#FFFFFF"),
                                "textSize": lit("10D"),
                                "bold": lit("true")
                            }
                        }
                    ],
                    "items": [
                        {
                            "properties": {
                                "fontColor": color(DARK_GREEN),
                                "background": color("#FFFFFF")
                            }
                        }
                    ],
                    "selection": [
                        {
                            "properties": {
                                "singleSelect": lit("true"),
                                "selectAllCheckboxEnabled": lit("false")
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
                                                                lit("'N/A'")
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
                                "show": lit("false")
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
        print(f"  + Updated {vp.parent.name} to Single-Select (Select all disabled, N/A pre-selected).")

def main():
    backup()
    apply_single_select()
    print("=== Complete! ===")

if __name__ == "__main__":
    main()
