#!/usr/bin/env python3
"""
clean_and_validate_all_schemas.py

Removes any accidental empty string keys created by shell interpolation,
ensures correct '$schema' is set, and validates every single visual
against the official Microsoft Fabric visualContainer schema.
"""

import json
import glob
import urllib.request
from pathlib import Path

SCHEMA_URL = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.12.0/schema.json"

def clean_and_validate():
    print("--- 1. Fetching official Fabric schema ---")
    req = urllib.request.Request(SCHEMA_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        schema = json.loads(resp.read().decode())
    print("  Official schema fetched successfully.")

    import jsonschema

    print("--- 2. Cleaning and validating all visual.json files ---")
    cleaned_count = 0
    valid_count = 0
    visual_files = glob.glob("development/jh_crowd_strike/CS_Dashboard/CS Dashboard.Report/definition/pages/*/visuals/*/visual.json")
    
    for path in visual_files:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        changed = False
        if "" in data:
            del data[""]
            changed = True
            cleaned_count += 1
        
        # Ensure $schema is set properly
        data["$schema"] = SCHEMA_URL
        changed = True

        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

        # Validate against schema
        try:
            jsonschema.validate(instance=data, schema=schema)
            valid_count += 1
        except jsonschema.ValidationError as err:
            print(f"  [ERROR] {path}: {err.message} at {list(err.path)}")

    print(f"  Cleaned {cleaned_count} files. {valid_count} / {len(visual_files)} visuals are 100% VALID.")

if __name__ == "__main__":
    clean_and_validate()
