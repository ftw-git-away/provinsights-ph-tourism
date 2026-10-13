"""Build provinsights.lvdash.json (Databricks AI/BI dashboard) from the dataset SQL in dashboard/datasets."""
import json, re, pathlib, itertools

DS_DIR = pathlib.Path("dashboard/datasets")
A = "tuklas_dev.`05_analytics`"

def sql_file(name):
    lines = DS_DIR.joinpath(name).read_text().splitlines()
    return "\n".join(l for l in lines if not l.lstrip().startswith("--")).strip()

def wrap(base_sql, where):
    return f"SELECT * FROM (\n{base_sql}\n) WHERE {where}"

ACT, CONC, REC, CMP, SEG, ECO, CAV = (sql_file(f) for f in [
    "01_activity.sql", "02_concentration.sql", "03_recovery.sql", "04_recovery_2022_vs_2023.sql",
    "05_segment_recovery.sql", "06_economy.sql", "07_unit_caveats.sql"])

datasets = {
    "ds_activity":          ("Activity (unit x year)", ACT),
    "ds_top_travelers":     ("Top 15 by travelers", wrap(ACT, "activity_eligible AND tourism_rank <= 15")),
    "ds_top_intensity":     ("Top 15 by intensity", wrap(ACT, "intensity_eligible AND intensity_rank <= 15")),
    "ds_bottom_travelers":  ("Bottom 15 by travelers", f"SELECT * FROM (SELECT *, MAX(tourism_rank) OVER (PARTITION BY year) AS lowest_rank FROM (\n{ACT}\n) WHERE activity_eligible) WHERE tourism_rank > lowest_rank - 15"),
    "ds_bottom_intensity":  ("Bottom 15 by intensity", f"SELECT * FROM (SELECT *, MAX(intensity_rank) OVER (PARTITION BY year) AS lowest_rank FROM (\n{ACT}\n) WHERE intensity_eligible) WHERE intensity_rank > lowest_rank - 15"),
    "ds_activity_excluded": ("Units not included", wrap(ACT, "NOT activity_eligible")),
    "ds_concentration":     ("Concentration (KPIs)", CONC),
    "ds_concentration_trend": ("Concentration (trend)", CONC),
    "ds_recovery":          ("Recovery (all units)", REC),
    "ds_recovery_eligible": ("Recovery (assessed units)", wrap(REC, "recovery_eligible")),
    "ds_recovery_excluded": ("Recovery (not assessed)", wrap(REC, "NOT recovery_eligible")),
    "ds_recovery_compare":  ("Recovery 2022 vs 2023", wrap(CMP, "recovery_index_2022 IS NOT NULL AND recovery_index_2023 IS NOT NULL")),
    "ds_segments":          ("Segments (all)", SEG),
    "ds_segments_cohort":   ("Segments (units below 2019)", wrap(SEG, "segment_analysis_cohort_flag AND eligible")),
    "ds_segments_mix":      ("Segments mix (units below 2019)", wrap(SEG, "segment_analysis_cohort_flag")),
    "ds_segments_excluded": ("Segments not assessed", wrap(SEG, "segment_analysis_cohort_flag AND NOT eligible")),
    "ds_economy":           ("Tourism x economy (all units)", ECO),
    "ds_economy_aligned":   ("Tourism x economy (assessed units)", wrap(ECO, "alignment_eligible")),
    "ds_economy_capped":    ("Very large tourism changes", wrap(ECO, "shown_at_chart_cap")),
    "ds_caveats":           ("Caveats", CAV),
}

ids = (f"w{n:03d}" for n in itertools.count(1))

def f(name, expr=None):
    return {"name": name, "expression": expr or f"`{name}`"}

def agg(fn, col):
    return f(f"{fn.lower()}({col})", f"{fn}(`{col}`)")

COUNT = f("count(*)", "COUNT(`*`)")

def q(ds, fields, disagg=False):
    return [{"name": "main_query", "query": {"datasetName": ds, "fields": fields, "disaggregated": disagg}}]

def frame(title, desc=None):
    fr = {"showTitle": True, "title": title}
    if desc:
        fr.update({"showDescription": True, "description": desc})
    return fr

def enc(field, kind, label):
    return {"fieldName": field, "scale": {"type": kind}, "displayName": label}

def counter(ds, field, title, desc=None):
    return {"name": next(ids), "queries": q(ds, [field]),
            "spec": {"version": 2, "widgetType": "counter",
                     "encodings": {"value": {"fieldName": field["name"], "displayName": title}},
                     "frame": frame(title, desc)}}

def bar(ds, x, y, title, color=None, horizontal=False, layout=None, desc=None, sort=True, ascending=False):
    fields = [x[0], y[0]] + ([color[0]] if color else [])
    cat, num = (y, x) if horizontal else (x, y)
    e_cat = enc(cat[0]["name"], "categorical", cat[1])
    if sort:
        axis = "x" if horizontal else "y"
        e_cat["scale"]["sort"] = {"by": axis if ascending else f"{axis}-reversed"}
    e_num = enc(num[0]["name"], "quantitative", num[1])
    encodings = {"x": e_num, "y": e_cat} if horizontal else {"x": e_cat, "y": e_num}
    if color:
        encodings["color"] = enc(color[0]["name"], "categorical", color[1])
    spec = {"version": 3, "widgetType": "bar", "encodings": encodings, "frame": frame(title, desc)}
    if layout:
        spec["mark"] = {"layout": layout}
    return {"name": next(ids), "queries": q(ds, fields), "spec": spec}

def line(ds, x, ys, title, desc=None):
    fields = [x[0]] + [y[0] for y in ys]
    return {"name": next(ids), "queries": q(ds, fields),
            "spec": {"version": 3, "widgetType": "line",
                     "encodings": {"x": enc(x[0]["name"], "categorical", x[1]),
                                   "y": {"scale": {"type": "quantitative"},
                                         "fields": [{"fieldName": y[0]["name"], "displayName": y[1]} for y in ys]}},
                     "frame": frame(title, desc)}}

def scatter(ds, x, y, color, title, desc=None):
    return {"name": next(ids), "queries": q(ds, [f(x[0]), f(y[0]), f(color[0])], disagg=True),
            "spec": {"version": 3, "widgetType": "scatter",
                     "encodings": {"x": enc(x[0], "quantitative", x[1]),
                                   "y": enc(y[0], "quantitative", y[1]),
                                   "color": enc(color[0], "categorical", color[1])},
                     "frame": frame(title, desc)}}

NUMFMT = {"integer": "0,0", "float": "0,0.0"}

def table(ds, cols, title, desc=None):
    columns = []
    for i, (name, label, typ) in enumerate(cols):
        c = {"fieldName": name, "booleanValues": ["false", "true"],
             "imageUrlTemplate": "{{ @ }}", "imageTitleTemplate": "{{ @ }}", "imageWidth": "", "imageHeight": "",
             "linkUrlTemplate": "{{ @ }}", "linkTextTemplate": "{{ @ }}", "linkTitleTemplate": "{{ @ }}",
             "linkOpenInNewTab": True, "type": typ,
             "displayAs": "number" if typ in NUMFMT else ("boolean" if typ == "boolean" else "string"),
             "visible": True, "order": 100000 + i, "title": label, "allowSearch": typ == "string",
             "alignContent": "right" if typ in NUMFMT else "left", "allowHTML": False,
             "highlightLinks": False, "useMonospaceFont": False, "preserveWhitespace": False,
             "displayName": name}
        if typ in NUMFMT:
            c["numberFormat"] = NUMFMT[typ]
        columns.append(c)
    return {"name": next(ids), "queries": q(ds, [f(c[0]) for c in cols], disagg=True),
            "spec": {"version": 1, "widgetType": "table", "encodings": {"columns": columns},
                     "invisibleColumns": [], "allowHTMLByDefault": False, "itemsPerPage": 25,
                     "paginationSize": "default", "condensed": True, "withRowNumber": False,
                     "frame": frame(title, desc)}}

def text(md):
    return {"name": next(ids), "multilineTextboxSpec": {"lines": [l + "\n" for l in md.strip().split("\n")]}}

def filt(kind, field, label, dss, default=None, dtype="STRING"):
    name = next(ids)
    queries, fields = [], []
    for ds in dss:
        qn = f"{name}_{ds}"
        queries.append({"name": qn, "query": {"datasetName": ds, "fields": [
            f(field), f(f"{field}_associativity", "COUNT_IF(`associative_filter_predicate_group`)")],
            "disaggregated": False}})
        fields.append({"fieldName": field, "displayName": label, "queryName": qn})
    spec = {"version": 2, "widgetType": kind, "encodings": {"fields": fields}, "frame": frame(label)}
    if default is not None:
        spec["selection"] = {"defaultSelection": {"values": {"dataType": dtype, "values": [{"value": str(default)}]}}}
    return {"name": name, "queries": queries, "spec": spec}

class Page:
    def __init__(self, name, title):
        self.name, self.title, self.layout, self.y = name, title, [], 0
    def row(self, height, *widgets):
        """Place widgets left to right on one row; each item is (widget, width)."""
        x = 0
        for w, width in widgets:
            self.layout.append({"widget": w, "position": {"x": x, "y": self.y, "width": width, "height": height}})
            x += width
        assert x <= 6, f"row too wide on {self.title}"
        self.y += height
    def to_json(self):
        return {"name": self.name, "displayName": self.title, "pageType": "PAGE_TYPE_CANVAS", "layout": self.layout}

DATA_NOTES = """
**Data notes:** Blank means DOT did not report the unit that year; it is never shown as 0. Where DOT printed "-" for a traveler category it is counted as 0. Aklan is not compared with 2019 because DOT changed how it counts Aklan from 2021. Totals cover included reporting units only, not the whole country. Patterns show association, not cause.
"""

# ---------- Page 1: Tourism Overview ----------
p1 = Page("p_overview", "1. Tourism Overview")
p1.row(2, (text("""
## Where is tourism activity highest?
100 reporting units: 82 provinces, 16 highly urbanized cities (HUCs), City of Isabela and NCR. **Tourism intensity** = travelers per 1,000 residents. Use the **Year** filter (default 2023).
"""), 4), (filt("filter-single-select", "year", "Year",
               ["ds_concentration", "ds_top_travelers", "ds_top_intensity", "ds_bottom_travelers", "ds_bottom_intensity", "ds_activity_excluded"],
               default=2023, dtype="INTEGER"), 2))
p1.row(3,
    (counter("ds_concentration", agg("SUM", "eligible_total_travelers"), "Travelers in included units",
             "Included reporting units only; not a national total"), 2),
    (counter("ds_concentration", agg("SUM", "eligible_reporting_unit_count"), "Units included"), 1),
    (counter("ds_concentration", agg("SUM", "excluded_reporting_unit_count"), "Units not included"), 1),
    (counter("ds_concentration", agg("SUM", "top_5_share_pct"), "Top 5 share (%)"), 1),
    (counter("ds_concentration", agg("SUM", "top_10_share_pct"), "Top 10 share (%)"), 1))
p1.row(9,
    (bar("ds_top_travelers", (agg("SUM", "total_travelers"), "Travelers"), (f("reporting_unit"), "Reporting unit"),
         "Top 15 units by travelers", color=(f("unit_type"), "Unit type"), horizontal=True), 3),
    (bar("ds_top_intensity", (agg("SUM", "tourism_intensity_per_1000"), "Travelers per 1,000 residents"),
         (f("reporting_unit"), "Reporting unit"), "Top 15 units by tourism intensity",
         color=(f("unit_type"), "Unit type"), horizontal=True), 3))
p1.row(9,
    (bar("ds_bottom_travelers", (agg("SUM", "total_travelers"), "Travelers"), (f("reporting_unit"), "Reporting unit"),
         "Lowest 15 units by travelers", color=(f("unit_type"), "Unit type"), horizontal=True, ascending=True,
         desc="Among units with reported data"), 3),
    (bar("ds_bottom_intensity", (agg("SUM", "tourism_intensity_per_1000"), "Travelers per 1,000 residents"),
         (f("reporting_unit"), "Reporting unit"), "Lowest 15 units by tourism intensity",
         color=(f("unit_type"), "Unit type"), horizontal=True, ascending=True,
         desc="Among units with reported data and population"), 3))
p1.row(7,
    (line("ds_concentration_trend", (f("year"), "Year"),
          [(agg("SUM", "top_5_share_pct"), "Top 5 share (%)"), (agg("SUM", "top_10_share_pct"), "Top 10 share (%)")],
          "How concentrated is tourism? Share of travelers in the top 5 and top 10 units",
          "All years; not affected by the Year filter"), 3),
    (table("ds_activity_excluded", [("reporting_unit", "Reporting unit", "string"), ("unit_type", "Unit type", "string"),
                                    ("data_status", "Data status", "string"),
                                    ("activity_exclusion_reason", "Why not included", "string")],
           "Units not included this year"), 3))
p1.row(2, (text(DATA_NOTES), 6))

# ---------- Page 2: Tourism Recovery ----------
p2 = Page("p_recovery", "2. Tourism Recovery")
p2.row(2, (text("""
## Which units are above or below 2019?
**Recovery index** = travelers in the comparison year / travelers in 2019 x 100. **100 = back to the 2019 level.**
"""), 2), (filt("filter-single-select", "comparison_year", "Comparison year",
               ["ds_recovery", "ds_recovery_eligible", "ds_recovery_excluded"], default=2023, dtype="INTEGER"), 2),
   (filt("filter-multi-select", "region_name", "Region",
         ["ds_recovery", "ds_recovery_eligible", "ds_recovery_excluded", "ds_recovery_compare"]), 2))
p2.row(7,
    (bar("ds_recovery", (f("recovery_status"), "Recovery status"), (COUNT, "Reporting units"),
         "Units above, below or not assessed against 2019", color=(f("recovery_status"), "Recovery status")), 2),
    (bar("ds_recovery", (f("region_name"), "Region"), (COUNT, "Reporting units"), "Recovery status by region",
         color=(f("recovery_status"), "Recovery status"), layout="stack", sort=False), 4))
p2.row(16,
    (bar("ds_recovery_eligible", (agg("SUM", "recovery_index"), "Recovery index (100 = 2019 level)"),
         (f("reporting_unit"), "Reporting unit"), "Recovery index by unit",
         color=(f("recovery_status"), "Recovery status"), horizontal=True), 3),
    (scatter("ds_recovery_compare", ("recovery_index_2022", "Recovery index 2022"),
             ("recovery_index_2023", "Recovery index 2023"), ("unit_type", "Unit type"),
             "2022 vs 2023: did units keep recovering?", "Above the diagonal = higher in 2023 than 2022. Not affected by Comparison year."), 3))
p2.row(6, (table("ds_recovery_excluded", [("reporting_unit", "Reporting unit", "string"), ("unit_type", "Unit type", "string"),
                                         ("recovery_exclusion_reason", "Why not assessed", "string")],
                 "Units not assessed and why"), 4), (text(DATA_NOTES), 2))

# ---------- Page 3: Traveler Recovery ----------
p3 = Page("p_segments", "3. Traveler Recovery")
p3.row(2, (text("""
## Which traveler groups are behind?
Units still **below 2019**, by traveler group. Foreign and overseas Filipino recovery appear once the Analytics fix in #65 lands.
"""), 2), (filt("filter-single-select", "comparison_year", "Comparison year",
               ["ds_segments_cohort", "ds_segments_mix", "ds_segments_excluded"], default=2023, dtype="INTEGER"), 2),
   (filt("filter-multi-select", "region_name", "Region", ["ds_segments_cohort", "ds_segments_mix", "ds_segments_excluded"]), 2))
p3.row(16,
    (bar("ds_segments_cohort", (agg("SUM", "recovery_index"), "Recovery index (100 = 2019 level)"),
         (f("reporting_unit"), "Reporting unit"), "Recovery index by traveler group",
         color=(f("segment"), "Traveler group"), horizontal=True, layout="group"), 3),
    (bar("ds_segments_mix", (agg("SUM", "travelers_comparison"), "Travelers in comparison year"),
         (f("reporting_unit"), "Reporting unit"), "Traveler mix in the comparison year",
         color=(f("segment"), "Traveler group"), horizontal=True, layout="stack"), 3))
p3.row(6, (table("ds_segments_excluded", [("reporting_unit", "Reporting unit", "string"), ("segment", "Traveler group", "string"),
                                         ("exclusion_reason", "Why not assessed", "string")],
                 "Traveler groups not assessed"), 6))

# ---------- Page 4: Tourism x Economy ----------
p4 = Page("p_economy", "4. Tourism x Economy")
p4.row(2, (text("""
## Do tourism and the local economy move together? (2019 to 2023)
Tourism = change in travelers. Economy = real growth in Accommodation and Food Services (A&F) output. **Provisional:** the pattern definition is pending team review.
"""), 3), (filt("filter-multi-select", "region_name", "Region", ["ds_economy", "ds_economy_aligned", "ds_economy_capped"]), 1),
   (filt("filter-multi-select", "unit_type", "Unit type", ["ds_economy", "ds_economy_aligned", "ds_economy_capped"]), 1),
   (filt("filter-multi-select", "pattern", "Pattern", ["ds_economy", "ds_economy_aligned", "ds_economy_capped"]), 1))
p4.row(7,
    (bar("ds_economy", (f("pattern"), "Pattern"), (COUNT, "Reporting units"), "Units by pattern",
         color=(f("alignment"), "Direction")), 3),
    (bar("ds_economy", (f("pattern"), "Pattern"), (agg("MEDIAN", "afs_share_of_gdp_pct"), "Median A&F share of GDP (%)"),
         "How big is A&F in the local economy, by pattern?", desc="Median share of GDP, 2023, current prices"), 3))
p4.row(10,
    (scatter("ds_economy_aligned", ("afs_gva_growth_pct", "Real A&F growth 2019-2023 (%)"),
             ("tourism_change_pct_chart", "Change in travelers 2019-2023 (%, capped at +300)"), ("pattern", "Pattern"),
             "Tourism change vs A&F growth", "Each dot is a reporting unit. Top-right = both up; top-left = tourism up, A&F down. Units above +300% sit at the top edge; exact values in the table below."), 3),
    (scatter("ds_economy_aligned", ("gdp_per_capita_current_2019", "GDP per capita 2019 (PHP)"),
             ("recovery_index_2023_chart", "Recovery index 2023 (capped at 400)"), ("unit_type", "Unit type"),
             "Is strong tourism recovery only in richer economies?",
             "Richer units are to the right. High dots on the left are strong recoveries outside the richest economies. Index above 400 sits at the top edge."), 3))
p4.row(5, (table("ds_economy_capped", [("reporting_unit", "Reporting unit", "string"),
                                       ("travelers_2019", "Travelers 2019", "integer"), ("travelers_2023", "Travelers 2023", "integer"),
                                       ("tourism_change_pct", "Change (%)", "float"), ("pattern", "Pattern", "string")],
                 "Very large changes (shown at the chart edge)",
                 "Mostly small 2019 bases. A minimum-base rule is pending in Analytics."), 6))
p4.row(8, (table("ds_economy", [("reporting_unit", "Reporting unit", "string"), ("unit_type", "Unit type", "string"),
                               ("pattern", "Pattern", "string"), ("tourism_change_pct", "Travelers change (%)", "float"),
                               ("afs_gva_growth_pct", "Real A&F growth (%)", "float"),
                               ("afs_share_of_gdp_pct", "A&F share of GDP (%)", "float"),
                               ("alignment_exclusion_reason", "Why not assessed", "string")],
                 "Units by pattern"), 4), (text(DATA_NOTES), 2))

# ---------- Page 5: Province Explorer ----------
p5 = Page("p_explorer", "5. Province Explorer")
p5.row(2, (text("""
## One reporting unit in one place
Pick a unit. Blank values mean the data was not reported or the measure does not apply.
"""), 4), (filt("filter-single-select", "reporting_unit", "Reporting unit",
               ["ds_economy", "ds_activity", "ds_segments", "ds_caveats"], default="Quezon"), 2))
p5.row(3,
    (counter("ds_economy", agg("SUM", "travelers_2023"), "Travelers 2023"), 1),
    (counter("ds_economy", agg("SUM", "tourism_change_pct"), "Travelers vs 2019 (%)"), 1),
    (counter("ds_economy", agg("SUM", "recovery_index_2023"), "Recovery index 2023"), 1),
    (counter("ds_economy", agg("SUM", "tourism_intensity_per_1000_2023"), "Travelers per 1,000 residents"), 1),
    (counter("ds_economy", agg("SUM", "afs_gva_growth_pct"), "Real A&F growth vs 2019 (%)"), 1),
    (counter("ds_economy", agg("SUM", "afs_share_of_gdp_pct"), "A&F share of GDP 2023 (%)"), 1))
p5.row(3, (table("ds_economy", [("reporting_unit", "Reporting unit", "string"), ("unit_type", "Unit type", "string"),
                               ("region_name", "Region", "string"), ("pattern", "Pattern", "string")],
                 "Unit"), 6))
p5.row(7,
    (line("ds_activity", (f("year"), "Year"), [(agg("SUM", "total_travelers"), "Travelers")], "Travelers 2019-2024",
          "Missing years are gaps, not zero"), 3),
    (bar("ds_segments", (f("segment"), "Traveler group"), (agg("SUM", "recovery_index"), "Recovery index"),
         "Recovery by traveler group (100 = 2019 level)", color=(f("comparison_year"), "Comparison year"),
         layout="group", sort=False), 3))
p5.row(7,
    (table("ds_activity", [("year", "Year", "integer"), ("total_travelers", "Travelers", "integer"),
                           ("population_total", "Population", "integer"),
                           ("tourism_intensity_per_1000", "Per 1,000 residents", "float"),
                           ("tourism_rank", "Rank", "integer"), ("data_status", "Data status", "string")],
           "Year by year"), 4),
    (table("ds_caveats", [("year", "Year", "integer"), ("caveat", "Caveat", "string")], "Caveats for this unit"), 2))

dashboard = {
    "datasets": [{"name": k, "displayName": v[0], "queryLines": [l + "\n" for l in v[1].split("\n")]}
                 for k, v in datasets.items()],
    "pages": [p.to_json() for p in (p1, p2, p3, p4, p5)],
}
out = pathlib.Path("dashboard/provinsights.lvdash.json")
out.write_text(json.dumps(dashboard, indent=2))
used = {qq["query"]["datasetName"] for p in dashboard["pages"] for l in p["layout"] for qq in l["widget"].get("queries", [])}
print("unused datasets:", set(datasets) - used, "| widgets:", sum(len(p["layout"]) for p in dashboard["pages"]))
