"""Docs and code agree on the data-quality check IDs (docs/data-quality-rules.md, section 6).

Only real checks count. In the notebooks: dq("ID", ...) calls in Silver, and DQ-GLD / DQ-ANL string
literals in Gold and Analytics code. Gold passes some IDs through a helper (compare_to_silver("DQ-GLD-05", ...)),
and Analytics maps result names to IDs (DQ_ID_BUILD in 01_build_analytics, DQ_ID_RULES in
02_analytics_validation), so a dq(...) call is not always there.
In the doc: the ID column of the table rows in section 6. Mentions in markdown, comments or prose do not count.

| Layer     | Notebooks               | How the ID appears in code    | Doc section              |
| --------- | ----------------------- | ----------------------------- | ------------------------ |
| Silver    | notebooks/02_silver     | dq("DQ-...", ...)             | 6.1 to 6.5               |
| Gold      | notebooks/03_gold       | "DQ-GLD-.." string literals   | 6.6 Gold (`DQ-GLD`)      |
| Analytics | notebooks/04_analytics  | "DQ-ANL-.." string literals   | 6.7 Analytics (`DQ-ANL`) |
"""
import ast
import re
import unittest

from _helpers import NOTEBOOKS, REPO_ROOT, dq_calls, load_notebook, python_cells

RULES_DOC = REPO_ROOT / "docs" / "data-quality-rules.md"
ROW_ID = re.compile(r"^\|\s*`?(DQ-[A-Z]+-\d+[a-z]?)`?\s*\|\s*([^|]*)\|", re.MULTILINE)
ID_STRING = {"gold": re.compile(r"DQ-GLD-\d+[a-z]?"), "analytics": re.compile(r"DQ-ANL-\d+[a-z]?")}
GOLD, ANALYTICS = "DQ-GLD-", "DQ-ANL-"
LAYERS = ("silver", "gold", "analytics")
FOLDERS = {"02_silver": "silver", "03_gold": "gold", "04_analytics": "analytics"}
# Notebook column in section 6.7 -> notebook file name
ANALYTICS_NOTEBOOKS = {"build": "01_build_analytics", "validation": "02_analytics_validation"}


def _section(text, start_pattern, end_pattern):
    start = re.search(start_pattern, text, re.MULTILINE)
    end = re.search(end_pattern, text[start.end():], re.MULTILINE) if start else None
    if not start or not end:
        raise ValueError(f"docs/data-quality-rules.md: section {start_pattern!r} not found or not closed")
    return text[start.end():start.end() + end.start()]


def _rows(part):
    """{check_id: Notebook column} for the table rows in part of the doc."""
    return {check_id: notebook.strip().strip("`") for check_id, notebook in ROW_ID.findall(part)}


def documented_checks():
    """({layer: {check_id: notebook column}}, [IDs in the wrong subsection]) from section 6."""
    text = RULES_DOC.read_text(encoding="utf-8")
    found = {
        "silver": _rows(_section(text, r"^## 6\b.*$", r"^### 6\.6\b")),
        "gold": _rows(_section(text, r"^### 6\.6\b.*$", r"^### 6\.7\b")),
        "analytics": _rows(_section(text, r"^### 6\.7\b.*$", r"^## 7\b")),
    }
    expected_layer = {i: ("gold" if i.startswith(GOLD) else "analytics" if i.startswith(ANALYTICS) else "silver")
                      for layer in LAYERS for i in found[layer]}
    misplaced = sorted(i for layer in LAYERS for i in found[layer] if expected_layer[i] != layer)
    return found, misplaced


def _string_ids(code, pattern):
    """Check IDs that appear as whole string literals in the code (ast ignores comments)."""
    return {node.value for node in ast.walk(ast.parse(code))
            if isinstance(node, ast.Constant) and isinstance(node.value, str) and pattern.fullmatch(node.value)}


def implemented_checks():
    """{layer: {check_id: {notebook names}}} from the notebooks."""
    found = {layer: {} for layer in LAYERS}
    for path in NOTEBOOKS:
        layer = FOLDERS.get(path.parent.name)
        if layer is None:
            continue
        for _, code in python_cells(load_notebook(path)):
            if layer in ID_STRING:
                ids = _string_ids(code, ID_STRING[layer])
            else:
                ids = {check_id for _, check_id, _ in dq_calls(code)}
            for check_id in ids:
                found[layer].setdefault(check_id, set()).add(path.stem)
    return found


class DocsAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documented, cls.misplaced = documented_checks()
        cls.implemented = implemented_checks()

    def test_found_checks_on_both_sides(self):
        for layer in LAYERS:
            with self.subTest(layer=layer):
                self.assertTrue(self.documented[layer], f"No {layer} checks found in section 6 of the doc")
                self.assertTrue(self.implemented[layer], f"No {layer} check IDs found in the notebooks")

    def test_ids_are_in_the_right_subsection(self):
        self.assertFalse(self.misplaced, "Move these IDs to the right part of section 6 (Silver in 6.1-6.5, "
                                         f"DQ-GLD in 6.6, DQ-ANL in 6.7): {self.misplaced}")

    def test_notebooks_use_their_layer_prefix(self):
        self.assertFalse(sorted(i for i in self.implemented["silver"] if i.startswith((GOLD, ANALYTICS))),
                         "Silver notebooks should not run DQ-GLD or DQ-ANL checks")
        self.assertFalse(sorted(i for i in self.implemented["gold"] if not i.startswith(GOLD)),
                         "Gold notebooks should only run DQ-GLD checks")

    def test_every_implemented_check_is_documented(self):
        for layer in LAYERS:
            with self.subTest(layer=layer):
                missing = sorted(set(self.implemented[layer]) - set(self.documented[layer]))
                self.assertFalse(missing, f"Add these {layer} checks to section 6 of "
                                          f"docs/data-quality-rules.md: {missing}")

    def test_every_documented_check_is_implemented(self):
        for layer in LAYERS:
            with self.subTest(layer=layer):
                missing = sorted(set(self.documented[layer]) - set(self.implemented[layer]))
                self.assertFalse(missing, f"These {layer} checks are documented in section 6 but no notebook "
                                          "runs them (implement them, or move them to 'Planned' / "
                                          f"'Draft IDs not used'): {missing}")

    def test_gold_and_analytics_notebook_column(self):
        """The Notebook column in 6.6 and 6.7 names the notebook that runs the check."""
        wrong = []
        for layer in ("gold", "analytics"):
            for check_id, label in self.documented[layer].items():
                notebook = ANALYTICS_NOTEBOOKS.get(label, label)
                runs_in = self.implemented[layer].get(check_id)
                if runs_in and notebook not in runs_in:
                    wrong.append(f"{check_id}: doc says {label}, runs in {sorted(runs_in)}")
        self.assertFalse(wrong, f"Fix the Notebook column in section 6: {wrong}")


if __name__ == "__main__":
    unittest.main()
