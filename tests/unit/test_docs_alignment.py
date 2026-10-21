"""Docs and code agree on the data-quality checks (docs/data-quality-rules.md, section 6).

Every check ID in a Silver, Gold or Analytics notebook must be a row in section 6 of the rules doc,
and every row there must be used by a notebook of the same layer.

Only real checks count. Mentions in markdown cells, comments or prose do not.
- Silver: dq("ID", ...) calls.
- Gold and Analytics: string literals that are exactly a check ID, such as dq("DQ-GLD-01", ...),
  compare_to_silver(fact, "DQ-GLD-05", ...), DQ_ID_BUILD = {"D1_dim_province": "DQ-ANL-01"} or
  ("lineage_nn_", "DQ-ANL-20"). Gold and Analytics pass some IDs through helpers and lookup tables,
  so their dq(...) calls alone don't show every ID.
"""
import ast
import re
import unittest

from _helpers import NOTEBOOKS, REPO_ROOT, dq_calls, load_notebook, python_cells

RULES_DOC = REPO_ROOT / "docs" / "data-quality-rules.md"
ROW_ID = re.compile(r"^\|\s*`?(DQ-[A-Z]+-\d+[a-z]?)`?\s*\|", re.MULTILINE)
CHECK_ID = re.compile(r"^DQ-[A-Z]+-\d+[a-z]?$")

# layer: (notebook folder, ID prefixes). Silver is every ID that is not Gold or Analytics.
GOLD = ("03_gold", ("DQ-GLD-",))
ANALYTICS = ("04_analytics", ("DQ-ANL-",))
NOT_SILVER = GOLD[1] + ANALYTICS[1]


def documented_checks():
    """IDs in the table rows of section 6 ('Checks by notebook'), up to section 7."""
    text = RULES_DOC.read_text(encoding="utf-8")
    start = re.search(r"^## 6\b.*$", text, re.MULTILINE)
    end = re.search(r"^## 7\b.*$", text, re.MULTILINE)
    if not start or not end:
        raise ValueError("docs/data-quality-rules.md: sections '## 6' and '## 7' not found")
    return set(ROW_ID.findall(text[start.end():end.start()]))


def id_literals(code):
    """Yield every string literal in the code that is exactly a check ID."""
    for node in ast.walk(ast.parse(code)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and CHECK_ID.match(node.value):
            yield node.value


def implemented_checks(folder, find_ids, prefixes=None):
    """{check_id: {notebook names}} for the notebooks in one folder, optionally only IDs with these prefixes."""
    found = {}
    for path in NOTEBOOKS:
        if path.parent.name != folder:
            continue
        for _, code in python_cells(load_notebook(path)):
            for check_id in find_ids(code):
                if prefixes is None or check_id.startswith(prefixes):
                    found.setdefault(check_id, set()).add(path.name)
    return found


def silver_ids(code):
    return (check_id for _, check_id, _ in dq_calls(code))


class DocsAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        documented = documented_checks()
        cls.layers = {
            "Silver": ({i for i in documented if not i.startswith(NOT_SILVER)},
                       implemented_checks("02_silver", silver_ids)),
            "Gold": ({i for i in documented if i.startswith(GOLD[1])},
                     implemented_checks(GOLD[0], id_literals, GOLD[1])),
            "Analytics": ({i for i in documented if i.startswith(ANALYTICS[1])},
                          implemented_checks(ANALYTICS[0], id_literals, ANALYTICS[1])),
        }

    def test_found_checks_on_both_sides(self):
        for layer, (documented, implemented) in self.layers.items():
            with self.subTest(layer=layer):
                self.assertTrue(documented, f"No {layer} checks found in section 6 of docs/data-quality-rules.md")
                self.assertTrue(implemented, f"No {layer} check IDs found in the {layer} notebooks")

    def test_every_implemented_check_is_documented(self):
        for layer, (documented, implemented) in self.layers.items():
            with self.subTest(layer=layer):
                missing = sorted(set(implemented) - documented)
                self.assertFalse(missing, f"Add these {layer} checks to section 6 of "
                                          f"docs/data-quality-rules.md: {missing}")

    def test_every_documented_check_is_implemented(self):
        for layer, (documented, implemented) in self.layers.items():
            with self.subTest(layer=layer):
                missing = sorted(documented - set(implemented))
                self.assertFalse(missing, f"These {layer} checks are documented in section 6 but no {layer} "
                                          "notebook uses them (implement them, or move them to 'Planned' / "
                                          f"'Draft IDs not used'): {missing}")


if __name__ == "__main__":
    unittest.main()
