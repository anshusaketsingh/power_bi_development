"""
apply_30_day_naming_rule.py

Rule: a measure/column carries a 30-day filter ONLY if "30 Days" is in its name.
1. Restores the 30-day filter on measure 'Closed Vulnerabilities (Last 30 Days)'.
2. Removes the 30-day cutoff from column 'Device Patch Exception'
   (Exception = device has no Microsoft closure at all).
Preserves CRLF line endings; takes a timestamped backup first.
"""
import shutil
import time
from pathlib import Path

BASE = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
TABLES = BASE / "development/jh_crowd_strike/CS_Dashboard/CS Dashboard.SemanticModel/definition/tables"
MEASURES = TABLES / "_Measures.tmdl"
FACT = TABLES / "crowdstrike_vulnerability_device_reporting.tmdl"


def rewrite(path, old, new):
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")
    assert old in text, f"Pattern not found in {path.name}"
    text = text.replace(old, new)
    if crlf:
        text = text.replace("\n", "\r\n")
    path.write_bytes(text.encode("utf-8"))
    print(f"Updated {path.name}")


def main():
    dest = BASE / "development/jh_crowd_strike/backups" / f"pre_30d_naming_rule_{time.strftime('%Y%m%d_%H%M%S')}"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(MEASURES, dest / MEASURES.name)
    shutil.copy2(FACT, dest / FACT.name)
    print(f"Backup: {dest}")

    rewrite(
        MEASURES,
        "\tmeasure 'Closed Vulnerabilities (Last 30 Days)' = [Closed Vulnerabilities]\n",
        """\tmeasure 'Closed Vulnerabilities (Last 30 Days)' =
\t\t\t// Remediated findings (distinct devices) closed in the last 30 days
\t\t\tVAR CutoffDate = TODAY() - 30
\t\t\tRETURN
\t\t\tCALCULATE(
\t\t\t\tDISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid]),
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Closed Date] >= CutoffDate
\t\t\t)
""",
    )

    rewrite(
        FACT,
        """\t\t\tVAR CutoffDate = TODAY() - 30
\t\t\tVAR LastMicrosoftClose =
\t\t\t\tCALCULATE(
\t\t\t\t\tMAX('crowdstrike_vulnerability_device_reporting'[Closed Date]),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t\tREMOVEFILTERS('Calendar')
\t\t\t\t)
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tSELECTEDVALUE('crowdstrike_vulnerability_device_reporting'[Platform]) = "Windows" && (
\t\t\t\t\tISBLANK(LastMicrosoftClose) || LastMicrosoftClose < CutoffDate
\t\t\t\t),""",
        """\t\t\tVAR LastMicrosoftClose =
\t\t\t\tCALCULATE(
\t\t\t\t\tMAX('crowdstrike_vulnerability_device_reporting'[Closed Date]),
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Platform] = "Windows",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[Vendor Normalized] = "Microsoft",
\t\t\t\t\t'crowdstrike_vulnerability_device_reporting'[status] = "Closed",
\t\t\t\t\tREMOVEFILTERS('Calendar')
\t\t\t\t)
\t\t\tRETURN
\t\t\tIF(
\t\t\t\tSELECTEDVALUE('crowdstrike_vulnerability_device_reporting'[Platform]) = "Windows" &&
\t\t\t\t\tISBLANK(LastMicrosoftClose),""",
    )


if __name__ == "__main__":
    main()
