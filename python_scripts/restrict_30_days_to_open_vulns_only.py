"""
restrict_30_days_to_open_vulns_only.py

Restricts 30-day cutoff logic exclusively to 'Open Vulnerabilities >30 Days':
1. Removes 30-day cutoff from 'Patching Rate %' -> DIVIDE([Closed Vulnerabilities], [Closed Vulnerabilities] + [Open Vulnerabilities], 0)
2. Removes 30-day cutoff from 'Closed Vulnerabilities (Last 30 Days)' -> points to [Closed Vulnerabilities]
3. Removes 30-day fallback from 'Vulnerabilities In Compliance' & 'Vulnerabilities Not In Compliance' -> returns BLANK() if no Time Frame Days is selected
4. Cleans up lingering 'Open Vulnerabilities Exceeding SLA' selector in v06_kpi_openover30d/visual.json
5. Preserves Windows CRLF (\\r\\n) line endings throughout.
"""

from pathlib import Path
import json
import shutil
import time

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
MEASURES_FILE = PROJ / "CS Dashboard.SemanticModel" / "definition" / "tables" / "_Measures.tmdl"
KPI_VISUAL_FILE = PROJ / "CS Dashboard.Report" / "definition" / "pages" / "47081098f92a957d7fd0" / "visuals" / "v06_kpi_openover30d" / "visual.json"
SCRIPT_FILE = BASE_DIR / "python_scripts" / "update_vulnerability_details_remediation_timeframes.py"

def backup():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BASE_DIR / "development" / "jh_crowd_strike" / "backups" / f"pre_30d_restriction_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    if MEASURES_FILE.exists():
        shutil.copy2(MEASURES_FILE, dest / "_Measures.tmdl")
    if KPI_VISUAL_FILE.exists():
        shutil.copy2(KPI_VISUAL_FILE, dest / "visual.json")
    print(f"Pre-flight backup saved to: {dest}")

def update_measures():
    with open(MEASURES_FILE, "rb") as f:
        raw_bytes = f.read()

    has_crlf = b"\r\n" in raw_bytes
    text = raw_bytes.decode("utf-8")

    # 1. Update Patching Rate %
    old_patching_rate = """\tmeasure 'Patching Rate %' = ```
			// Metric 5: Closed (Last 30 Days) / (Closed Last 30 Days + Open > 30 Days)
			VAR CutoffDate = TODAY() - 30
			VAR ClosedInPeriod = 
				CALCULATE(
					DISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
					'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
					'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
					'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
					'crowdstrike_vulnerability_device_reporting'[Closed Date] >= CutoffDate
				)
			VAR OpenOlderThan30 = [Open Vulnerabilities >30 Days]
			VAR Workload = ClosedInPeriod + OpenOlderThan30
			RETURN
			DIVIDE(ClosedInPeriod, Workload, 0)
			```"""

    new_patching_rate = """\tmeasure 'Patching Rate %' = ```
			// Patching Rate: Closed Devices / Total Workload (Closed + Open)
			VAR ClosedDevices = [Closed Vulnerabilities]
			VAR OpenDevices = [Open Vulnerabilities]
			VAR Workload = ClosedDevices + OpenDevices
			RETURN
			DIVIDE(ClosedDevices, Workload, 0)
			```"""

    assert old_patching_rate.replace("\r\n", "\n") in text.replace("\r\n", "\n"), "Patching Rate % pattern not found!"
    text = text.replace("\r\n", "\n").replace(old_patching_rate.replace("\r\n", "\n"), new_patching_rate.replace("\r\n", "\n"))

    # 2. Update Closed Vulnerabilities (Last 30 Days)
    old_closed_30d = """\tmeasure 'Closed Vulnerabilities (Last 30 Days)' =
			// Metric 5 Count View: Remediated findings during the previous period
			VAR CutoffDate = TODAY() - 30
			RETURN
			CALCULATE(
				DISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
				'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
				'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
				'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
				'crowdstrike_vulnerability_device_reporting'[Closed Date] >= CutoffDate
			)"""

    new_closed_30d = """\tmeasure 'Closed Vulnerabilities (Last 30 Days)' = [Closed Vulnerabilities]"""

    assert old_closed_30d.replace("\r\n", "\n") in text.replace("\r\n", "\n"), "Closed Vulnerabilities (Last 30 Days) pattern not found!"
    text = text.replace(old_closed_30d.replace("\r\n", "\n"), new_closed_30d.replace("\r\n", "\n"))

    # 3. Update Vulnerabilities In Compliance (remove 30d fallback)
    old_in_comp = """\tmeasure 'Vulnerabilities In Compliance' =
			VAR TDays = SELECTEDVALUE('Remediation Time Frame'[Time Frame Days])
			RETURN
			IF(
				ISBLANK(TDays),
				CALCULATE(
					DISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
					'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
				'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
					'crowdstrike_vulnerability_device_reporting'[status] = "Open",
					'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= 30
				),
				CALCULATE(
					DISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
					'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
				'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
					'crowdstrike_vulnerability_device_reporting'[status] = "Open",
					'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= TDays
				)
			)"""

    new_in_comp = """\tmeasure 'Vulnerabilities In Compliance' =
			VAR TDays = SELECTEDVALUE('Remediation Time Frame'[Time Frame Days])
			RETURN
			IF(
				ISBLANK(TDays),
				BLANK(),
				CALCULATE(
					DISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
					'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
					'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
					'crowdstrike_vulnerability_device_reporting'[status] = "Open",
					'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= TDays
				)
			)"""

    assert old_in_comp.replace("\r\n", "\n") in text.replace("\r\n", "\n"), "Vulnerabilities In Compliance pattern not found!"
    text = text.replace(old_in_comp.replace("\r\n", "\n"), new_in_comp.replace("\r\n", "\n"))

    # 4. Update Vulnerabilities Not In Compliance (remove 30d fallback)
    old_not_in_comp = """\tmeasure 'Vulnerabilities Not In Compliance' =
			VAR TDays = SELECTEDVALUE('Remediation Time Frame'[Time Frame Days])
			RETURN
			IF(
				ISBLANK(TDays),
				CALCULATE(
					DISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
					'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
				'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
					'crowdstrike_vulnerability_device_reporting'[status] = "Open",
					'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] > 30
				),
				CALCULATE(
					DISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
					'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
				'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
					'crowdstrike_vulnerability_device_reporting'[status] = "Open",
					'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] > TDays
				)
			)"""

    new_not_in_comp = """\tmeasure 'Vulnerabilities Not In Compliance' =
			VAR TDays = SELECTEDVALUE('Remediation Time Frame'[Time Frame Days])
			RETURN
			IF(
				ISBLANK(TDays),
				BLANK(),
				CALCULATE(
					DISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
					'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
					'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
					'crowdstrike_vulnerability_device_reporting'[status] = "Open",
					'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] > TDays
				)
			)"""

    assert old_not_in_comp.replace("\r\n", "\n") in text.replace("\r\n", "\n"), "Vulnerabilities Not In Compliance pattern not found!"
    text = text.replace(old_not_in_comp.replace("\r\n", "\n"), new_not_in_comp.replace("\r\n", "\n"))

    # Restore CRLF
    normalized = text.replace("\n", "\r\n")
    with open(MEASURES_FILE, "wb") as f:
        f.write(normalized.encode("utf-8"))

    print(f"Successfully updated {MEASURES_FILE} with 30-day logic restricted solely to 'Open Vulnerabilities >30 Days'.")

def update_visual_kpi():
    if not KPI_VISUAL_FILE.exists():
        return
    with open(KPI_VISUAL_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # replace any metadata selector referencing Open Vulnerabilities Exceeding SLA
    data_str = json.dumps(data)
    if "Open Vulnerabilities Exceeding SLA" in data_str:
        data_str = data_str.replace("Open Vulnerabilities Exceeding SLA", "Open Vulnerabilities >30 Days")
        with open(KPI_VISUAL_FILE, "w", encoding="utf-8") as f:
            f.write(data_str)
        print(f"Cleaned metadata selector in {KPI_VISUAL_FILE}")

def update_script():
    if not SCRIPT_FILE.exists():
        return
    text = SCRIPT_FILE.read_text(encoding="utf-8")
    text = text.replace("{FACT}[Vulnerability Age Days] <= 30", "{FACT}[Vulnerability Age Days] <= TDays")
    text = text.replace("{FACT}[Vulnerability Age Days] > 30", "{FACT}[Vulnerability Age Days] > TDays")
    SCRIPT_FILE.write_text(text, encoding="utf-8")
    print(f"Updated {SCRIPT_FILE}")

def main():
    backup()
    update_measures()
    update_visual_kpi()
    update_script()

if __name__ == "__main__":
    main()
