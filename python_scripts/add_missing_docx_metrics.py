"""
add_missing_docx_metrics.py
Explicitly adds all exact measures specified in Crowdstrike Metric Definition.docx:
1. Metric 1: 'Critical & High Vulnerabilities' (severity in Critical/High or base_score >= 7.0)
2. Metric 5 Count View: 'Closed Vulnerabilities (Last 30 Days)'
3. Metric 6: 'Systems Not Rebooted in More Than 30 Days' (reporting_last_reboot < TODAY() - 30)
Synchronizes into both CS Dashboard.SemanticModel and CS Dashboard.pbix archive.
"""

import os
from pathlib import Path

BASE_DIR = Path("development/jh_crowd_strike/CS_Dashboard")
MEAS_FILE = BASE_DIR / "CS Dashboard.SemanticModel" / "definition" / "tables" / "_Measures.tmdl"
PBIX_PATH = Path("development/jh_crowd_strike/CS Dashboard.pbix")
REP_DIR = BASE_DIR / "CS Dashboard.Report"

with open(MEAS_FILE, "r", encoding="utf-8") as f:
    content = f.read()

new_measures = """
\tmeasure 'Critical & High Vulnerabilities' = ```
\t\t// Metric 1: Count open vulnerabilities classified as High or Critical based on severity or CVSS score
\t\tCALCULATE(
\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open",
\t\t\t'crowdstrike_vulnerability_device_reporting'[severity] IN { "Critical", "High" }
\t\t\t\t|| 'crowdstrike_vulnerability_device_reporting'[base_score] >= 7.0
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'Closed Vulnerabilities (Last 30 Days)' = ```
\t\t// Metric 5 Count View: Remediated findings during the previous 30-day period
\t\tCALCULATE(
\t\t\tCOUNTROWS('crowdstrike_vulnerability_device_reporting'),
\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t'crowdstrike_vulnerability_device_reporting'[Closed Date] >= (TODAY() - 30)
\t\t)
\t\t```
\t\tformatString: #,##0

\tmeasure 'Systems Not Rebooted in More Than 30 Days' = ```
\t\t// Metric 6: Count devices where the most recent reboot occurred >30 days ago
\t\tVAR CutoffDate = TODAY() - 30
\t\tRETURN
\t\tCALCULATE(
\t\t\tDISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t'crowdstrike_vulnerability_device_reporting'[reporting_last_reboot] < CutoffDate
\t\t\t\t|| ISBLANK('crowdstrike_vulnerability_device_reporting'[reporting_last_reboot])
\t\t)
\t\t```
\t\tformatString: #,##0
"""

if "Critical & High Vulnerabilities" not in content:
    idx = content.find("\tcolumn Dummy")
    if idx != -1:
        updated = content[:idx] + new_measures + "\n" + content[idx:]
    else:
        updated = content + "\n" + new_measures
    with open(MEAS_FILE, "w", encoding="utf-8") as f:
        f.write(updated)
    print("Added docx metrics to _Measures.tmdl")
else:
    print("Metrics already present in _Measures.tmdl")

# Synchronize PBIX if exists
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
