"""Docs stay in step with the code: every Silver DQ check ID is listed in docs/data-quality-rules.md."""
import re
import unittest

from _helpers import NOTEBOOKS, REPO_ROOT

DQ_ID = re.compile(r"DQ-[A-Z]+-\d+[a-z]?")
RULES_DOC = REPO_ROOT / "docs" / "data-quality-rules.md"


class DocsAlignmentTests(unittest.TestCase):
    def test_every_silver_dq_check_is_documented(self):
        documented = set(DQ_ID.findall(RULES_DOC.read_text(encoding="utf-8")))
        silver = [path for path in NOTEBOOKS if path.parent.name == "03_silver"]
        self.assertTrue(silver, "No Silver notebooks found")
        for path in silver:
            used = set(DQ_ID.findall(path.read_text(encoding="utf-8")))
            with self.subTest(notebook=path.name):
                missing = sorted(used - documented)
                self.assertFalse(missing, f"Add these checks to docs/data-quality-rules.md: {missing}")


if __name__ == "__main__":
    unittest.main()
