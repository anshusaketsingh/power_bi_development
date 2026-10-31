"""
fix_sla_slicer_filter_ast.py

Fixes the SQInExpr filter AST in the SLA Threshold slicers:
Replaces invalid nested {"expr": {"Literal": ...}} with proper SQExpr {"Literal": {"Value": "'N/A'"}}.
"""

import json
from pathlib import Path

BASE_DIR = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE_DIR / "development" / "jh_crowd_strike" / "CS_Dashboard"
REPORT_PAGES = PROJ / "CS Dashboard.Report" / "definition" / "pages"

VISUAL_PATHS = [
    REPORT_PAGES / "47081098f92a957d7fd0" / "visuals" / "v13_slicer_sla_thresh" / "visual.json",
    REPORT_PAGES / "p02_trends_exceptions" / "visuals" / "p2_v13_slicer_sla_thresh" / "visual.json",
    REPORT_PAGES / "p03_vulnerability_details" / "visuals" / "p3_v13_slicer_sla_thresh" / "visual.json",
    REPORT_PAGES / "p05_vulnerability_details" / "visuals" / "p5_v13_slicer_sla_thresh" / "visual.json"
]

def fix_slicers():
    for vp in VISUAL_PATHS:
        if not vp.exists():
            continue
        data = json.loads(vp.read_text(encoding="utf-8"))
        
        # Check and fix general filter
        try:
            general = data["visual"]["objects"]["general"]
            for g in general:
                flt = g.get("properties", {}).get("filter", {}).get("filter", {})
                where = flt.get("Where", [])
                for w in where:
                    in_expr = w.get("Condition", {}).get("In", {})
                    values = in_expr.get("Values", [])
                    # Fix values: must be [[ {"Literal": {"Value": "'N/A'"}} ]]
                    fixed_values = []
                    for row in values:
                        fixed_row = []
                        for cell in row:
                            if "expr" in cell and "Literal" in cell["expr"]:
                                fixed_row.append(cell["expr"])
                            else:
                                fixed_row.append(cell)
                        fixed_values.append(fixed_row)
                    in_expr["Values"] = fixed_values
            
            vp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"  + Fixed filter AST in {vp.parent.name}")
        except Exception as e:
            print(f"  ! Error fixing {vp}: {e}")

if __name__ == "__main__":
    fix_slicers()
