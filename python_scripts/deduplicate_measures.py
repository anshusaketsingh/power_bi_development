"""
deduplicate_measures.py

Removes measures that are exact duplicates of another measure and repoints every
report reference (visuals, pages) and model reference to the canonical measure.

  Open Vulnerabilities  <-  Total Vulnerabilities, Hosts with Vulnerabilities,
                            Open Vulnerabilities in Scope, Open Vulnerabilities by SLA Bucket
  New Vulnerabilities   <-  In-Scope Vulnerabilities

Visual labels are preserved by writing the old name as the projection displayName.
Preserves CRLF in TMDL; takes a timestamped backup first.
"""
import json
import re
import shutil
import time
from pathlib import Path

BASE = Path("/Users/Saket - Personal/Studies/Git Directory/power_bi_development")
PROJ = BASE / "development/jh_crowd_strike/CS_Dashboard"
MEASURES = PROJ / "CS Dashboard.SemanticModel/definition/tables/_Measures.tmdl"
REPORT_DEF = PROJ / "CS Dashboard.Report/definition"

CANON = {
    "Total Vulnerabilities": "Open Vulnerabilities",
    "Hosts with Vulnerabilities": "Open Vulnerabilities",
    "Open Vulnerabilities in Scope": "Open Vulnerabilities",
    "Open Vulnerabilities by SLA Bucket": "Open Vulnerabilities",
    "In-Scope Vulnerabilities": "New Vulnerabilities",
}


def backup(files):
    dest = BASE / "development/jh_crowd_strike/backups" / f"pre_dedupe_measures_{time.strftime('%Y%m%d_%H%M%S')}"
    for f in files:
        rel = f.relative_to(PROJ)
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest / rel)
    print(f"Backup: {dest}")


def fix_node(node, stats):
    """Recursively repoint references. Returns nothing; mutates in place."""
    if isinstance(node, dict):
        # Measure field expression
        if "Measure" in node and isinstance(node["Measure"], dict):
            prop = node["Measure"].get("Property")
            if prop in CANON:
                node["Measure"]["Property"] = CANON[prop]
                stats["field"] += 1
        # Projection: queryRef / nativeQueryRef
        if "queryRef" in node and "field" in node:
            q = node["queryRef"]
            if isinstance(q, str) and q.startswith("_Measures."):
                old = q[len("_Measures."):]
                if old in CANON:
                    node["queryRef"] = "_Measures." + CANON[old]
                    if node.get("nativeQueryRef") == old:
                        node["nativeQueryRef"] = CANON[old]
                    node.setdefault("displayName", node.get("nativeQueryRef") and old or old)
                    node["displayName"] = old
                    stats["proj"] += 1
        for k, v in list(node.items()):
            if isinstance(v, str) and v.startswith("_Measures.") and v[len("_Measures."):] in CANON:
                node[k] = "_Measures." + CANON[v[len("_Measures."):]]
                stats["ref"] += 1
            else:
                fix_node(v, stats)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            if isinstance(v, str) and v.startswith("_Measures.") and v[len("_Measures."):] in CANON:
                node[i] = "_Measures." + CANON[v[len("_Measures."):]]
                stats["ref"] += 1
            else:
                fix_node(v, stats)


def update_report():
    changed = []
    for p in REPORT_DEF.rglob("*.json"):
        text = p.read_text(encoding="utf-8")
        if not any(old in text for old in CANON):
            continue
        data = json.loads(text)
        stats = {"field": 0, "proj": 0, "ref": 0}
        fix_node(data, stats)
        if sum(stats.values()):
            changed.append((p, stats))
    return changed


def update_model():
    raw = MEASURES.read_bytes().decode("utf-8")
    text = raw.replace("\r\n", "\n")
    lines = text.split("\n")
    out, skip = [], False
    for ln in lines:
        m = re.match(r"\tmeasure '([^']+)'", ln)
        if m:
            skip = m.group(1) in CANON
            if skip:
                print(f"  - removed measure: {m.group(1)}")
        elif re.match(r"\t(column|partition) ", ln):
            skip = False
        if not skip:
            out.append(ln)
    text = "\n".join(out)
    # remaining DAX references
    for old, new in CANON.items():
        text = text.replace(f"[{old}]", f"[{new}]")
    MEASURES.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))


def main():
    targets = [MEASURES]
    for p in REPORT_DEF.rglob("*.json"):
        if any(old in p.read_text(encoding="utf-8") for old in CANON):
            targets.append(p)
    backup(targets)

    changed = update_report()
    for p, s in changed:
        data = json.loads(p.read_text(encoding="utf-8"))
        fix_node(data, {"field": 0, "proj": 0, "ref": 0})
        p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  ~ {p.relative_to(REPORT_DEF)}  {s}")
    update_model()
    print("Done.")


if __name__ == "__main__":
    main()
