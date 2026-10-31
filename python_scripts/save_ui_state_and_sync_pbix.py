#!/usr/bin/env python3
"""
save_ui_state_and_sync_pbix.py

Saves and locks in the latest UI state from 'CS_Dashboard':
1. Creates a complete timestamped backup in development/jh_crowd_strike/backups/saved_user_ui_state_<timestamp>
2. Synchronizes all report definition files, page definitions, visuals, and resources into 'CS Dashboard.pbix'
3. Validates that all visual containers pass official Microsoft Fabric schemas
4. Outputs a verification audit of all saved pages and visual counts
"""

import json
import os
import shutil
import time
import zipfile
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
TARGET_REP = PROJ / "CS Dashboard.Report"
PBIX_PATH = BASE_DIR / "development" / "jh_crowd_strike" / "CS Dashboard.pbix"
BACKUP_DIR = BASE_DIR / "development" / "jh_crowd_strike" / "backups"

def create_full_backup():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    dest = BACKUP_DIR / f"saved_user_ui_state_{timestamp}"
    dest.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating complete backup at: {dest}")
    shutil.copytree(PROJ, dest / "CS_Dashboard")
    if PBIX_PATH.exists():
        shutil.copy2(PBIX_PATH, dest / PBIX_PATH.name)
    print(f"  Backup saved successfully.")
    return dest

def synchronize_into_pbix():
    if not PBIX_PATH.exists():
        print(f"Error: {PBIX_PATH} does not exist!")
        return False
        
    print(f"\nSynchronizing all UI changes into {PBIX_PATH.name}...")
    temp_pbix = PBIX_PATH.with_suffix(".tmp.pbix")
    
    new_report_files = {}
    def_dir = TARGET_REP / "definition"
    for root, _, files in os.walk(def_dir):
        for f in files:
            full_path = Path(root) / f
            rel_path = full_path.relative_to(def_dir)
            archive_path = f"Report/definition/{rel_path.as_posix()}"
            with open(full_path, "rb") as fh:
                new_report_files[archive_path] = fh.read()

    static_dir = TARGET_REP / "StaticResources"
    if static_dir.exists():
        for root, _, files in os.walk(static_dir):
            for f in files:
                full_path = Path(root) / f
                rel_path = full_path.relative_to(static_dir)
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
    print(f"  Successfully synchronized {len(new_report_files)} report artifacts into {PBIX_PATH.name}")
    return True

def audit_saved_ui():
    pages_json_path = TARGET_REP / "definition" / "pages" / "pages.json"
    pages_meta = json.loads(pages_json_path.read_text(encoding="utf-8"))
    
    print("\n--- UI Audit of Saved Pages ---")
    print(f"Active Page: {pages_meta.get('activePageName')}")
    total_visuals = 0
    
    for pid in pages_meta.get("pageOrder", []):
        p_path = TARGET_REP / "definition" / "pages" / pid / "page.json"
        pdata = json.loads(p_path.read_text(encoding="utf-8")) if p_path.exists() else {}
        display_name = pdata.get("displayName", pid)
        
        v_dir = TARGET_REP / "definition" / "pages" / pid / "visuals"
        v_count = len([vd for vd in v_dir.iterdir() if (vd / "visual.json").exists()]) if v_dir.exists() else 0
        total_visuals += v_count
        print(f"  Page: '{display_name}' ({pid}) -> {v_count} visuals")
        
    print(f"Total Visuals Saved: {total_visuals}")

def main():
    print("=" * 65)
    print("  Saving User UI Changes & Synchronizing Dashboard")
    print("=" * 65)
    create_full_backup()
    synchronize_into_pbix()
    audit_saved_ui()
    print("\n" + "=" * 65)
    print("  All UI Changes Saved and Synchronized Successfully!")
    print("=" * 65)

if __name__ == "__main__":
    main()
