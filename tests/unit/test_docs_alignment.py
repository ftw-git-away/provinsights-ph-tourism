"""Docs and code agree on the Silver data-quality checks (docs/data-quality-rules.md, section 6).

Only real checks count: dq("ID", ...) calls in the notebooks, and table rows in section 6 of the doc.
Mentions in markdown, comments or prose do not.
"""
import re
import unittest

from _helpers import NOTEBOOKS, REPO_ROOT, dq_calls, load_notebook, python_cells

RULES_DOC = REPO_ROOT / "docs" / "data-quality-rules.md"
ROW_ID = re.compile(r"^\|\s*`?(DQ-[A-Z]+-\d+[a-z]?)`?\s*\|", re.MULTILINE)


def documented_silver_checks():
    """IDs in the table rows of section 6 ('Checks by notebook'), up to section 7."""
    text = RULES_DOC.read_text(encoding="utf-8")
    start = re.search(r"^## 6\b.*$", text, re.MULTILINE)
    end = re.search(r"^## 7\b.*$", text, re.MULTILINE)
    if not start or not end:
        raise ValueError("docs/data-quality-rules.md: sections '## 6' and '## 7' not found")
    return set(ROW_ID.findall(text[start.end():end.start()]))


def implemented_silver_checks():
    """{check_id: {notebook names}} for every dq("ID", ...) call in the Silver notebooks."""
    found = {}
    for path in NOTEBOOKS:
        if path.parent.name != "03_silver":
            continue
        for _, code in python_cells(load_notebook(path)):
            for _, check_id, _ in dq_calls(code):
                found.setdefault(check_id, set()).add(path.name)
    return found


class DocsAlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documented = documented_silver_checks()
        cls.implemented = implemented_silver_checks()

    def test_found_checks_on_both_sides(self):
        self.assertTrue(self.documented, "No checks found in section 6 of docs/data-quality-rules.md")
        self.assertTrue(self.implemented, "No dq(...) calls found in the Silver notebooks")

    def test_every_implemented_check_is_documented(self):
        missing = sorted(set(self.implemented) - self.documented)
        self.assertFalse(missing, f"Add these checks to section 6 of docs/data-quality-rules.md: {missing}")

    def test_every_documented_check_is_implemented(self):
        missing = sorted(self.documented - set(self.implemented))
        self.assertFalse(missing, "These checks are documented in section 6 but no Silver notebook runs them "
                                  f"(implement them, or move them to 'Planned' / 'Draft IDs not used'): {missing}")


if __name__ == "__main__":
    unittest.main()
