"""Sync the dataset SQL in dashboard/datasets/ into dashboard/provinsights.lvdash.json.

The page layout lives in the exported JSON (edit it in Databricks, then Export dashboard).
The SQL lives in dashboard/datasets/*.sql. This script copies each file's SQL into the
matching dataset of the JSON, so the two never drift apart.

Each .sql file starts with a header:
    -- dataset: ds_profile
    -- display: Province profile, 2023 (Query 3 with group names)
    -- source:  ...
    -- used by: ...
The header lines are not sent to Databricks; everything after them is the query.

Usage (from the repository root):
    python dashboard/tools/build_lvdash.py           # update the JSON
    python dashboard/tools/build_lvdash.py --check   # fail if the JSON and the SQL differ (for CI)
"""
import json, pathlib, re, sys

ROOT = pathlib.Path("dashboard")
DS_DIR = ROOT / "datasets"
OUT = ROOT / "provinsights.lvdash.json"
CATALOG, SCHEMA = "tuklas_dev", "05_analytics"
QUERY3_FILES = ["05_profile_2023.sql", "06_aq3_corr.sql", "07_aq3_table.sql", "08_aq4_table.sql"]


def read_sql(path):
    header, body, in_header = {}, [], True
    for line in path.read_text().splitlines():
        m = re.match(r"--\s*(dataset|display|source|used by):\s*(.*)", line)
        if in_header and m:
            header[m.group(1)] = m.group(2).strip()
            continue
        in_header = False
        body.append(line)
    if "dataset" not in header:
        sys.exit(f"{path}: missing '-- dataset:' header")
    return header, "\n".join(body).strip()


def query3_block(sql):
    """The document's Query 3 (leading -> classified CTEs) must be identical in every file that uses it."""
    start, end = sql.find("WITH leading AS ("), sql.find("labelled AS (")
    return sql[start:end] if start >= 0 and end > start else None


def main(check=False):
    dash = json.loads(OUT.read_text())
    existing = {d["name"]: d for d in dash["datasets"]}
    datasets, blocks = [], {}
    for f in sorted(DS_DIR.glob("*.sql")):
        h, sql = read_sql(f)
        d = dict(existing.get(h["dataset"], {"name": h["dataset"]}))
        d.update(displayName=h.get("display", h["dataset"]),
                 queryLines=[l + "\n" for l in sql.split("\n")],
                 catalog=CATALOG, schema=SCHEMA)
        datasets.append(d)
        if f.name in QUERY3_FILES:
            blocks[f.name] = query3_block(sql)

    if len(set(blocks.values())) > 1 or None in blocks.values():
        sys.exit(f"Query 3 differs between {', '.join(QUERY3_FILES)}: change them together")

    names = {d["name"] for d in datasets}
    used = {q["query"]["datasetName"] for p in dash["pages"] for item in p["layout"]
            for q in item["widget"].get("queries", [])}
    if used - names:
        sys.exit(f"widgets use datasets with no .sql file: {sorted(used - names)}")
    if names - used:
        print(f"warning: datasets not used by any widget: {sorted(names - used)}")

    new = dict(dash, datasets=datasets)
    if check:
        if json.loads(OUT.read_text()) != new:
            sys.exit("provinsights.lvdash.json is out of date: run python dashboard/tools/build_lvdash.py")
        print(f"OK: {len(datasets)} datasets match dashboard/datasets/")
        return
    OUT.write_text(json.dumps(new, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT}: {len(datasets)} datasets, {sum(len(p['layout']) for p in dash['pages'])} widgets")


if __name__ == "__main__":
    main(check="--check" in sys.argv)
