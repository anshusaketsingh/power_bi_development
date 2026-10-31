"""
simplify_measures_with_branching.py

Simplifies all measures in _Measures.tmdl using Measure Branching:
[In-Scope Vulnerabilities] is the single source of truth for scope (Windows + Microsoft).
Other measures branch off [In-Scope Vulnerabilities] and [Open Vulnerabilities]
instead of repeating CALCULATE(DISTINCTCOUNT(aid), Platform="Windows", Vendor="Microsoft").

Preserves Windows CRLF (\\r\\n) line endings throughout.
"""

from pathlib import Path
import shutil
import time

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
MEASURES_FILE = PROJ / "CS Dashboard.SemanticModel" / "definition" / "tables" / "_Measures.tmdl"

def backup():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BASE_DIR / "development" / "jh_crowd_strike" / "backups" / f"pre_measure_branching_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    if MEASURES_FILE.exists():
        shutil.copy2(MEASURES_FILE, dest / "_Measures.tmdl")
    print(f"Pre-flight backup saved to: {dest}")
    return dest

def build_measures_tmdl():
    content = """table _Measures
\tlineageTag: 52e21a31-a892-4138-8bc2-7a1e324b906d

\tmeasure 'In-Scope Vulnerabilities' =
\t\t\t// Base measure: Total in-scope Microsoft Windows devices
\t\t\tCALCULATE(
\t\t\t\tDISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft"
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: e09fd127-8bd8-4385-8bf2-9803af8cbe97

\tmeasure 'Open Vulnerabilities' =
\t\t\t// Open Microsoft Windows devices
\t\t\tCALCULATE(
\t\t\t\t[In-Scope Vulnerabilities],
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Open"
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 0ec3aee5-15e6-4ef3-b050-f1a008dd53ac

\tmeasure 'CISA KEV Vulnerabilities' =
\t\t\t// Metric 2: Open CISA KEV devices
\t\t\tCALCULATE(
\t\t\t\t[In-Scope Vulnerabilities],
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[is_cisa_kev] = TRUE()
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 9ccf8ae5-c55e-4adc-a3f1-2ee0aa5d4cd7

\tmeasure 'CISA KEV %' =
\t\t\t// CISA KEV as percentage of open findings
\t\t\tDIVIDE([CISA KEV Vulnerabilities], [Open Vulnerabilities], 0)
\t\tformatString: 0.0%
\t\tlineageTag: 247a865b-92c1-47c9-8e1c-ddf762acc33d

\tmeasure 'Closed Vulnerabilities' =
\t\t\t// Closed Microsoft Windows devices
\t\t\tCALCULATE(
\t\t\t\t[In-Scope Vulnerabilities],
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed"
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: b308fdab-59b2-4b2b-86ac-438c0740e311

\tmeasure 'New Vulnerabilities' =
\t\t\t// New findings by period on Calendar
\t\t\t[In-Scope Vulnerabilities]
\t\tformatString: #,##0
\t\tlineageTag: 6fd8bd1e-5be8-4a26-8f97-f3fe3820ffc9

\tmeasure 'Closed Vulnerabilities by Closed Date' =
\t\t\t// Closed findings activated via USERELATIONSHIP
\t\t\tCALCULATE(
\t\t\t\t[In-Scope Vulnerabilities],
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\tUSERELATIONSHIP('Calendar'[Date], 'crowdstrike_vulnerability_device_reporting'[Closed Date])
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 570cdc77-25a3-4147-9984-725ed7ccf8a7

\tmeasure 'Remediation Rate %' = DIVIDE([Closed Vulnerabilities by Closed Date], [New Vulnerabilities], 0)
\t\tformatString: 0.0%
\t\tlineageTag: 5972c945-30b2-41d0-8d83-68c6ea513558

\tmeasure 'Net Vulnerability Change' = [New Vulnerabilities] - [Closed Vulnerabilities by Closed Date]
\t\tformatString: 0
\t\tlineageTag: fe939f3e-6407-407f-b56c-c0a2d5700717

\tmeasure 'Patching Rate %' = ```
\t\t\t// Patching Rate: Closed Devices / Total Workload (Closed + Open)
\t\t\tVAR ClosedDevices = [Closed Vulnerabilities]
\t\t\tVAR OpenDevices = [Open Vulnerabilities]
\t\t\tVAR Workload = ClosedDevices + OpenDevices
\t\t\tRETURN
\t\t\tDIVIDE(ClosedDevices, Workload, 0)
\t\t\t```
\t\tformatString: 0.0%
\t\tlineageTag: 01ba75a5-8541-44a5-a6d9-cbe774b6986f

\tmeasure 'Patching Rate' = [Closed Vulnerabilities]
\t\tformatString: #,##0
\t\tlineageTag: 5d289923-bbf4-46d0-ab86-2d651af73c01

\tmeasure 'Devices No Microsoft Remediation 30 Days' =
\t\t\tVAR CutoffDate = TODAY() - 30
\t\t\tRETURN
\t\t\tCOUNTROWS(
\t\t\t\tFILTER(
\t\t\t\t\tVALUES('crowdstrike_vulnerability_device_reporting'[aid]),
\t\t\t\t\tVAR LastMicrosoftClose =
\t\t\t\t\t\tCALCULATE(
\t\t\t\t\t\t\tMAX('crowdstrike_vulnerability_device_reporting'[Closed Date]),
\t\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t\t\t\tREMOVEFILTERS('Calendar')
\t\t\t\t\t\t)
\t\t\t\t\tRETURN
\t\t\t\t\t\tISBLANK(LastMicrosoftClose) || LastMicrosoftClose < CutoffDate
\t\t\t\t)
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: dad29aa2-617f-4a6e-a1fd-c0626ddebe79

\tmeasure 'Critical & High Vulnerabilities' =
\t\t\t// Metric 1: Open Critical or High severity findings
\t\t\tCALCULATE(
\t\t\t\t[Open Vulnerabilities],
\t\t\t\t('crowdstrike_vulnerability_device_reporting'[cve_severity] IN { "Critical", "High" }
\t\t\t\t\t|| 'crowdstrike_vulnerability_device_reporting'[cve_base_score] >= 7.0)
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 3cdbb094-7fd2-423c-875e-179715882585

\tmeasure 'Closed Vulnerabilities (Last 30 Days)' =
\t\t\t// Remediated findings (distinct devices) closed in the last 30 days
\t\t\tVAR CutoffDate = TODAY() - 30
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\t[Closed Vulnerabilities],
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Closed Date] >= CutoffDate
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 3d14a51c-0899-4b0d-bd60-4bce0423ccbc

\tmeasure 'Systems Not Rebooted in More Than 30 Days' =
\t\t\tVAR CutoffDate = TODAY() - 30
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\tDISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[reporting_last_reboot] < CutoffDate
\t\t\t\t\t|| ISBLANK('crowdstrike_vulnerability_device_reporting'[reporting_last_reboot])
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: b53e1058-e8d0-49d8-9de7-1bb26ae4b2ea

\tmeasure 'Open Vulnerabilities >30 Days' =
\t\t\t// Metric 3: Open Microsoft Windows findings older than 30 days
\t\t\tVAR CutoffDate = TODAY() - 30
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\t[Open Vulnerabilities],
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Created Date] <= CutoffDate
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 36db6a06-451b-4cdf-8f2f-7251ec6337b2

\tmeasure 'Total Remediations' = [Closed Vulnerabilities]
\t\tformatString: #,##0
\t\tlineageTag: ba77b285-4a47-4341-acde-90debec46dfb

\tmeasure 'Hosts with Critical & High Vulns (Last 90 Days)' =
\t\t\t// Open Critical/High ExPRT findings first seen in last 90 days
\t\t\tCALCULATE(
\t\t\t\t[Open Vulnerabilities],
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[ExPRT Rating] IN { "Critical", "High" },
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Created Date] >= TODAY() - 90
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 58a19587-9690-4f3f-841d-143d30aed376

\tmeasure 'ExPRT Time Frame' =
\t\t\tVAR d = SELECTEDVALUE('crowdstrike_vulnerability_device_reporting'[ExPRT Time Frame Days])
\t\t\tRETURN IF(NOT(ISBLANK(d)), d & " days")
\t\tlineageTag: 32cfecbc-d823-4f48-b1b2-63c6e5c02bd4

\tmeasure 'In Compliance %' =
\t\t\tVAR InC = CALCULATE([Open Vulnerabilities], 'crowdstrike_vulnerability_device_reporting'[ExPRT Compliance] = "In compliance")
\t\t\tVAR NotC = CALCULATE([Open Vulnerabilities], 'crowdstrike_vulnerability_device_reporting'[ExPRT Compliance] = "Not in compliance")
\t\t\tRETURN DIVIDE(InC, InC + NotC)
\t\tformatString: 0%
\t\tlineageTag: 683cf4d3-a4b4-44a4-99c8-34f340524c5a

\tmeasure 'Not in Compliance %' =
\t\t\tVAR InC = CALCULATE([Open Vulnerabilities], 'crowdstrike_vulnerability_device_reporting'[ExPRT Compliance] = "In compliance")
\t\t\tVAR NotC = CALCULATE([Open Vulnerabilities], 'crowdstrike_vulnerability_device_reporting'[ExPRT Compliance] = "Not in compliance")
\t\t\tRETURN DIVIDE(NotC, InC + NotC)
\t\tformatString: 0%
\t\tlineageTag: 057e8429-2bce-4ea3-89b1-7db6b2cca556

\tmeasure 'First Seen on Hosts (Days)' =
\t\t\t// Days since the CVE was first seen on any in-scope host
\t\t\tVAR FirstSeen = CALCULATE(MIN('crowdstrike_vulnerability_device_reporting'[Created Date]), 'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft")
\t\t\tRETURN IF(NOT(ISBLANK(FirstSeen)), DATEDIFF(FirstSeen, TODAY(), DAY))
\t\tformatString: 0 "days"
\t\tlineageTag: e469aa68-5986-4fa4-ad30-0e32dd8e6e1b

\tmeasure 'Vulnerabilities In Compliance' =
\t\t\tVAR TDays = SELECTEDVALUE('Remediation Time Frame'[Time Frame Days])
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tISBLANK(TDays),
\t\t\t\tBLANK(),
\t\t\t\tCALCULATE(
\t\t\t\t\t[Open Vulnerabilities],
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] <= TDays
\t\t\t\t)
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: 8ddb8518-2867-4ece-b1e4-c5dc9ca92210

\tmeasure 'Vulnerabilities Not In Compliance' =
\t\t\tVAR TDays = SELECTEDVALUE('Remediation Time Frame'[Time Frame Days])
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tISBLANK(TDays),
\t\t\t\tBLANK(),
\t\t\t\tCALCULATE(
\t\t\t\t\t[Open Vulnerabilities],
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vulnerability Age Days] > TDays
\t\t\t\t)
\t\t\t)
\t\tformatString: #,##0
\t\tlineageTag: dfd69f49-3f77-41ad-b863-969dcb905d98

\tmeasure 'Time Frame In Compliance %' =
\t\t\tVAR InC = [Vulnerabilities In Compliance]
\t\t\tVAR NotC = [Vulnerabilities Not In Compliance]
\t\t\tVAR TotalOpen = InC + NotC
\t\t\tRETURN
\t\t\tDIVIDE(InC, TotalOpen, 0)
\t\tformatString: 0.0%
\t\tlineageTag: 343708e3-db8e-4c79-acc0-939ba392ab21

\tmeasure 'Time Frame Not In Compliance %' =
\t\t\tVAR InC = [Vulnerabilities In Compliance]
\t\t\tVAR NotC = [Vulnerabilities Not In Compliance]
\t\t\tVAR TotalOpen = InC + NotC
\t\t\tRETURN
\t\t\tDIVIDE(NotC, TotalOpen, 0)
\t\tformatString: 0.0%
\t\tlineageTag: 64f9b517-ee90-4b5d-a8ae-53dc68641a29

\tcolumn Dummy
\t\tisHidden
\t\tlineageTag: ad85f6eb-57e2-4f7e-8c5f-79d9c08ffb6d
\t\tsourceColumn: [Dummy]

\tpartition _Measures = calculated
\t\tmode: import
\t\tsource = ROW("Dummy", BLANK())
"""
    # Write with CRLF line endings
    crlf_content = content.replace("\r\n", "\n").replace("\n", "\r\n")
    MEASURES_FILE.write_bytes(crlf_content.encode("utf-8"))
    print(f"Successfully updated {MEASURES_FILE} with simplified measure branching.")

def main():
    backup()
    build_measures_tmdl()

if __name__ == "__main__":
    main()
