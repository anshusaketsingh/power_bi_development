"""
update_measures_to_distinctcount_aid.py

Updates all core vulnerability and compliance measures in _Measures.tmdl to use:
    DISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid])
instead of:
    COUNTROWS('crowdstrike_vulnerability_device_reporting')

Preserves Windows CRLF (\\r\\n) line endings throughout.
"""

from pathlib import Path
import re

MEASURES_FILE = Path("development/jh_crowd_strike/CS_Dashboard/CS Dashboard.SemanticModel/definition/tables/_Measures.tmdl")

def main():
    with open(MEASURES_FILE, "rb") as f:
        raw_bytes = f.read()

    has_crlf = b"\r\n" in raw_bytes
    text = raw_bytes.decode("utf-8")

    # Replace COUNTROWS('crowdstrike_vulnerability_device_reporting')
    target = "COUNTROWS('crowdstrike_vulnerability_device_reporting')"
    replacement = "DISTINCTCOUNT('crowdstrike_vulnerability_device_reporting'[aid])"

    count = text.count(target)
    print(f"Found {count} occurrences of {target}")

    new_text = text.replace(target, replacement)

    # Ensure CRLF line endings
    if has_crlf:
        normalized = new_text.replace("\r\n", "\n").replace("\n", "\r\n")
    else:
        normalized = new_text

    with open(MEASURES_FILE, "wb") as f:
        f.write(normalized.encode("utf-8"))

    print(f"Successfully updated {MEASURES_FILE} with {count} replacements.")

    # Also update python_scripts/update_vulnerability_details_remediation_timeframes.py
    script_file = Path("python_scripts/update_vulnerability_details_remediation_timeframes.py")
    if script_file.exists():
        s_text = script_file.read_text(encoding="utf-8")
        s_text_updated = s_text.replace("COUNTROWS({FACT})", "DISTINCTCOUNT({FACT}[aid])")
        script_file.write_text(s_text_updated, encoding="utf-8")
        print(f"Updated {script_file} with DISTINCTCOUNT logic.")

if __name__ == "__main__":
    main()
