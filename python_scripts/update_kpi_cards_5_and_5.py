#!/usr/bin/env python3
"""
update_kpi_cards_5_and_5.py

Updates the KPI card rows on Executive Summary and Remediation Compliance:
- Sets exactly 5 cards on Executive Summary (Risk Posture & Hygiene)
- Sets exactly 5 cards on Remediation Compliance (Patching Performance & Workload)
- Eliminates duplicate cards between the two tabs
- Adds a new card for 'Patched Vulnerabilities' on Remediation Compliance
- Positions all 5 cards uniformly on both tabs:
    x = 345, 657, 969, 1281, 1593 (w = 292 px, gap = 20 px, y = 125, h = 115)
- Standardizes visual styling (rounded corners, dark green titles, shadows)
- Backs up report files and synchronizes into 'CS Dashboard.pbix'
"""

import json
import os
import shutil
import time
import uuid
import zipfile
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
TARGET_REP = PROJ / "CS Dashboard.Report"
PAGES_DIR = TARGET_REP / "definition" / "pages"
PBIX_PATH = BASE_DIR / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"
BACKUP_DIR = BASE_DIR / "development" / "jh_crowd_strike" / "backups"

EXEC_PAGE_ID = "47081098f92a957d7fd0"
REMED_PAGE_ID = "p03_vulnerability_details"

# Standard horizontal positions for 5 cards across 1540px content area
# (width=292, gap=20 -> total width = 5*292 + 4*20 = 1460 + 80 = 1540)
CARD_POSITIONS = [
    {"x": 345, "y": 125, "width": 292, "height": 115},
    {"x": 657, "y": 125, "width": 292, "height": 115},
    {"x": 969, "y": 125, "width": 292, "height": 115},
    {"x": 1281, "y": 125, "width": 292, "height": 115},
    {"x": 1593, "y": 125, "width": 292, "height": 115},
]

def create_backup():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"pre_kpi_5_and_5_sync_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(PAGES_DIR, dest / "pages")
    if PBIX_PATH.exists():
        shutil.copy2(PBIX_PATH, dest / PBIX_PATH.name)
    print(f"Pre-flight backup created at: {dest}")
    return dest

def make_card_visual(name, pos, measure_name, title_text, z_order=7000, tab_order=7000, display_name=None):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": name,
        "position": {
            "x": pos["x"],
            "y": pos["y"],
            "z": z_order,
            "height": pos["height"],
            "width": pos["width"],
            "tabOrder": tab_order
        },
        "visual": {
            "visualType": "cardVisual",
            "query": {
                "queryState": {
                    "Data": {
                        "projections": [
                            {
                                "field": {
                                    "Measure": {
                                        "Expression": {
                                            "SourceRef": {
                                                "Entity": "_Measures"
                                            }
                                        },
                                        "Property": measure_name
                                    }
                                },
                                "queryRef": f"_Measures.{measure_name}",
                                "nativeQueryRef": measure_name,
                                **({"displayName": display_name} if display_name else {})
                            }
                        ]
                    }
                }
            },
            "objects": {
                "outline": [
                    {
                        "properties": {
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "false"
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
                            },
                            "width": {
                                "expr": {
                                    "Literal": {
                                        "Value": "1D"
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
                ],
                "title": [
                    {
                        "properties": {
                            "text": {
                                "expr": {
                                    "Literal": {
                                        "Value": f"'{title_text}'"
                                    }
                                }
                            },
                            "show": {
                                "expr": {
                                    "Literal": {
                                        "Value": "true"
                                    }
                                }
                            },
                            "titleWrap": {
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
                                                "Value": "'#1b4332'"
                                            }
                                        }
                                    }
                                }
                            },
                            "fontSize": {
                                "expr": {
                                    "Literal": {
                                        "Value": "13D"
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
                "dropShadow": [
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
                    }
                ]
            }
        },
        "filterConfig": {
            "filters": [
                {
                    "name": uuid.uuid4().hex[:20],
                    "field": {
                        "Measure": {
                            "Expression": {
                                "SourceRef": {
                                  "Entity": "_Measures"
                                }
                            },
                            "Property": measure_name
                        }
                    },
                    "type": "Advanced"
                }
            ]
        }
    }

def update_executive_summary():
    print("\n--- Updating Executive Summary (5 Cards) ---")
    page_vis_dir = PAGES_DIR / EXEC_PAGE_ID / "visuals"
    
    # 1. Delete duplicate card: Patching Rate % (v08_kpi_patchrate00)
    dup_path = page_vis_dir / "v08_kpi_patchrate00"
    if dup_path.exists():
        shutil.rmtree(dup_path)
        print("  Deleted duplicate card 'v08_kpi_patchrate00' (Patching Rate %) from Executive Summary.")

    # 2. Configure 5 target cards in order
    exec_cards = [
        ("v05_kpi_openvulns00", "Critical & High Vulnerabilities", "Critical & High Vulnerabilities", 7000),
        ("v07_kpi_cisakev0000", "CISA KEV Vulnerabilities", "CISA KEV Vulnerabilities", 8000),
        ("v06_kpi_openover30d", "Open Vulnerabilities >30 Days", "Open Vulnerabilities > 30 Days", 9000),
        ("v14_kpi_reboot30d", "Systems Not Rebooted in More Than 30 Days", "Systems Not Rebooted > 30 Days", 10000),
        ("v09_kpi_devexcept00", "Device-Level 30-Day Exception", "Device-Level 30-Day Exceptions", 11000),
    ]

    for idx, (folder_name, measure_name, title_text, z_order) in enumerate(exec_cards):
        pos = CARD_POSITIONS[idx]
        v_data = make_card_visual(folder_name, pos, measure_name, title_text, z_order=z_order, tab_order=z_order)
        dest_dir = page_vis_dir / folder_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "visual.json").write_text(json.dumps(v_data, indent=2), encoding="utf-8")
        print(f"  Card {idx+1}: {folder_name} -> '{title_text}' at x={pos['x']}, w={pos['width']}")

def update_remediation_compliance():
    print("\n--- Updating Remediation Compliance (5 Cards) ---")
    page_vis_dir = PAGES_DIR / REMED_PAGE_ID / "visuals"

    # 1. Delete duplicate cards: Critical & High, CISA KEV
    for dup in ["p3_kpi_crit_high", "p3_kpi_cisa_kev"]:
        dup_path = page_vis_dir / dup
        if dup_path.exists():
            shutil.rmtree(dup_path)
            print(f"  Deleted duplicate card '{dup}' from Remediation Compliance.")

    # 2. Configure 5 target cards in order
    remed_cards = [
        ("p3_kpi_open_total", "Open Vulnerabilities", "Total Open Findings in Scope", 7000),
        ("p3_kpi_patched_vulns", "Patched Vulnerabilities", "Patched Vulnerabilities", 8000),
        ("p3_kpi_patch_rate", "Patching Rate %", "Remediation Rate %", 9000),
        ("p3_kpi_in_scope", "In-Scope Vulnerabilities", "In-Scope Workload", 10000),
        ("p3_kpi_closed_30d", "Closed Vulnerabilities (Last 30 Days)", "Closed (Last 30 Days)", 11000),
    ]

    for idx, (folder_name, measure_name, title_text, z_order) in enumerate(remed_cards):
        pos = CARD_POSITIONS[idx]
        v_data = make_card_visual(folder_name, pos, measure_name, title_text, z_order=z_order, tab_order=z_order)
        dest_dir = page_vis_dir / folder_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        (dest_dir / "visual.json").write_text(json.dumps(v_data, indent=2), encoding="utf-8")
        print(f"  Card {idx+1}: {folder_name} -> '{title_text}' at x={pos['x']}, w={pos['width']}")

def synchronize_pbix():
    if not PBIX_PATH.exists():
        print(f"Warning: {PBIX_PATH} does not exist, skipping pbix sync.")
        return
        
    print(f"\nSynchronizing updated definition into {PBIX_PATH.name}...")
    temp_pbix = PBIX_PATH.with_suffix(".tmp.pbix")
    
    new_report_files = {}
    for root, _, files in os.walk(TARGET_REP / "definition"):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(TARGET_REP / "definition")
            archive_path = f"Report/definition/{rel_path.as_posix()}"
            with open(full_path, "rb") as fh:
                new_report_files[archive_path] = fh.read()

    if (TARGET_REP / "StaticResources").exists():
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
    print(f"  Successfully synchronized into {PBIX_PATH.name}")

def main():
    print("=" * 65)
    print("  Updating KPI Cards to 5 and 5 with Zero Duplicates")
    print("=" * 65)
    create_backup()
    update_executive_summary()
    update_remediation_compliance()
    synchronize_pbix()
    print("\n" + "=" * 65)
    print("  KPI Cards Updated & Synchronized Successfully!")
    print("=" * 65)

if __name__ == "__main__":
    main()
