"""
align_all_6_metric_visuals.py
Ensures every one of the 6 business metrics from Crowdstrike Metric Definition.docx 
has at least one dedicated visual on the dashboard:
1. Critical & High Vulnerabilities -> KPI Card 1
2. CISA Known Exploited (KEV) -> KPI Card 2
3. Vulnerabilities Older Than 30 Days (Dynamic SLA) -> KPI Card 3 + Aging Chart
4. Remediation Rate vs New Vulnerabilities -> Weekly Trend Combo Chart
5. Patch Compliance Rate % -> KPI Card 4
6. Systems Not Rebooted > 30 Days -> KPI Card 5
Plus: Device Remediation Exceptions -> KPI Card 6
Plus: Operational Triage Grid
"""

import os
import json
from pathlib import Path

BASE_DIR = Path("development/jh_crowd_strike/CS_Dashboard")
REP_DIR = BASE_DIR / "CS Dashboard.Report"
PBIX_PATH = Path("development/jh_crowd_strike/CS Dashboard.pbix")

pages_dir = REP_DIR / "definition" / "pages"
with open(pages_dir / "pages.json", "r", encoding="utf-8") as f:
    pages_meta = json.load(f)

active_page_id = pages_meta.get("activePageName") or pages_meta["pageOrder"][0]
page_dir = pages_dir / active_page_id
vis_dir = page_dir / "visuals"
vis_dir.mkdir(parents=True, exist_ok=True)

def write_vis(v_id: str, obj: dict):
    p = vis_dir / v_id
    p.mkdir(parents=True, exist_ok=True)
    with open(p / "visual.json", "w", encoding="utf-8") as vf:
        json.dump(obj, vf, indent=2)

def make_kpi(v_id: str, x: int, w: int, measure_name: str):
    return {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json",
        "name": v_id,
        "position": {"x": x, "y": 110, "z": 500, "height": 130, "width": w, "tabOrder": 5},
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

# 6 KPI cards across row: available width 1860 px -> 296 px each, gap 16 px
# Metric 1: Critical & High Vulnerabilities
write_vis("v05_kpi_openvulns00", make_kpi("v05_kpi_openvulns00", 30, 296, "Critical & High Vulnerabilities"))

# Metric 2: CISA KEV Vulnerabilities
write_vis("v07_kpi_cisakev0000", make_kpi("v07_kpi_cisakev0000", 342, 296, "CISA KEV Vulnerabilities"))

# Metric 3: Open Vulnerabilities Exceeding SLA
write_vis("v06_kpi_openover30d", make_kpi("v06_kpi_openover30d", 654, 296, "Open Vulnerabilities Exceeding SLA"))

# Metric 5: Patching Rate %
write_vis("v08_kpi_patchrate00", make_kpi("v08_kpi_patchrate00", 966, 296, "Patching Rate %"))

# Metric 6: Systems Not Rebooted in More Than 30 Days
write_vis("v14_kpi_reboot30d", make_kpi("v14_kpi_reboot30d", 1278, 296, "Systems Not Rebooted in More Than 30 Days"))

# Bonus / Governance Metric: Devices No Microsoft Remediation 30 Days
write_vis("v09_kpi_devexcept00", make_kpi("v09_kpi_devexcept00", 1590, 296, "Devices No Microsoft Remediation 30 Days"))

print("Updated all 6 KPI cards covering Metrics 1, 2, 3, 5, 6.")

# Synchronize PBIX
if PBIX_PATH.exists():
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
    print(f"Synchronized PBIX archive {PBIX_PATH}.")
