"""
adjust_slicer_gaps_uniformly.py

Adjusts vertical positions of slicers on Executive Summary and Remediation tab
to remove the gap left where the SLA threshold slicer was deleted, making the
spacing uniform (pitch of 82px: height 72px + 10px margin):

1. Executive Summary (47081098f92a957d7fd0):
   - v02_slicer_platform0:  y = 125
   - v03_slicer_vendor000:   y = 207
   - v04_slicer_weekstart:   y = 289
   - v15_slicer_severity:    y = 371 (was 453)
   - v16_slicer_cisakev:     y = 453 (was 535)
   - v17_slicer_devexcept:   y = 535 (was 617)

2. Remediation Compliance (p03_vulnerability_details):
   - p3_slicer_week:         y = 125
   - p3_slicer_severity:     y = 207
   - p3_slicer_exception:    y = 289
   - p3_slicer_platform:     y = 371
   - p3_slicer_cisakev:      y = 453
   - p3_slicer_exprt:        y = 535 (was 617)
"""

import json
from pathlib import Path
import shutil
import time

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
PAGES_DIR = PROJ / "CS Dashboard.Report" / "definition" / "pages"

def backup(files):
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BASE_DIR / "development" / "jh_crowd_strike" / "backups" / f"pre_slicer_spacing_adjust_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    for f in files:
        rel = f.relative_to(PROJ)
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest / rel)
    print(f"Pre-flight backup to: {dest}")
    return dest

def set_y(visual_file, new_y):
    with open(visual_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    old_y = data["position"]["y"]
    data["position"]["y"] = new_y
    with open(visual_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  {visual_file.parent.name}: y changed from {old_y} -> {new_y}")

def main():
    exec_page = PAGES_DIR / "47081098f92a957d7fd0" / "visuals"
    remed_page = PAGES_DIR / "p03_vulnerability_details" / "visuals"

    targets = [
        exec_page / "v15_slicer_severity" / "visual.json",
        exec_page / "v16_slicer_cisakev" / "visual.json",
        exec_page / "v17_slicer_devexcept" / "visual.json",
        remed_page / "p3_slicer_exprt" / "visual.json",
    ]

    backup(targets)

    print("Adjusting Executive Summary slicers:")
    set_y(exec_page / "v15_slicer_severity" / "visual.json", 371)
    set_y(exec_page / "v16_slicer_cisakev" / "visual.json", 453)
    set_y(exec_page / "v17_slicer_devexcept" / "visual.json", 535)

    print("Adjusting Remediation tab slicers:")
    set_y(remed_page / "p3_slicer_exprt" / "visual.json", 535)

    print("Slicer positions updated successfully.")

if __name__ == "__main__":
    main()
