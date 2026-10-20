"""Python checks on every notebook: structure, syntax and shared conventions."""
import ast
import json
import re
import unittest

from _helpers import NOTEBOOKS, cell_source, dq_calls, load_notebook, python_cells

ALLOWED_CATALOG = "tuklas_dev"
ALLOWED_SEVERITIES = {"BLOCK", "REVIEW", "LOG"}   # docs/data-quality-rules.md
VALID_CELL_TYPES = {"code", "markdown", "raw"}
SECRET_PATTERNS = [
    re.compile(r"dapi[0-9a-f]{32}"),                       # Databricks personal access token
    re.compile(r"ghp_[A-Za-z0-9]{36}"),                    # GitHub token
    re.compile(r"(?i)(password|secret|token)\s*=\s*['\"][^'\"]{8,}['\"]"),
]


class NotebookPythonTests(unittest.TestCase):
    def test_notebooks_exist(self):
        self.assertTrue(NOTEBOOKS, "No notebooks found under notebooks/")

    def test_notebooks_are_valid_json_with_valid_cells(self):
        for path in NOTEBOOKS:
            with self.subTest(notebook=path.name):
                try:
                    notebook = load_notebook(path)
                except json.JSONDecodeError as exc:
                    self.fail(f"{path.name} is not valid JSON: {exc}")
                self.assertIsInstance(notebook.get("cells"), list, "'cells' must be a list")
                for index, cell in enumerate(notebook["cells"], start=1):
                    self.assertIn(cell.get("cell_type"), VALID_CELL_TYPES, f"cell {index} has an invalid cell_type")

    def test_every_notebook_has_a_markdown_cell(self):
        for path in NOTEBOOKS:
            with self.subTest(notebook=path.name):
                notebook = load_notebook(path)
                self.assertTrue(any(cell.get("cell_type") == "markdown" for cell in notebook["cells"]))

    def test_python_cells_compile(self):
        for path in NOTEBOOKS:
            notebook = load_notebook(path)
            for index, code in python_cells(notebook):
                with self.subTest(notebook=path.name, cell=index):
                    try:
                        ast.parse(code, filename=f"{path.name}:cell-{index}")
                    except SyntaxError as exc:
                        self.fail(f"{path.name} cell {index}: {exc}")

    def test_catalog_is_tuklas_dev(self):
        for path in NOTEBOOKS:
            notebook = load_notebook(path)
            for index, code in python_cells(notebook):
                for match in re.finditer(r"^\s*CATALOG\s*=\s*['\"]([^'\"]+)['\"]", code, re.MULTILINE):
                    with self.subTest(notebook=path.name, cell=index):
                        self.assertEqual(match.group(1), ALLOWED_CATALOG)

    def test_no_secrets_in_notebooks(self):
        for path in NOTEBOOKS:
            notebook = load_notebook(path)
            for index, cell in enumerate(notebook["cells"], start=1):
                source = cell_source(cell)
                for pattern in SECRET_PATTERNS:
                    with self.subTest(notebook=path.name, cell=index, pattern=pattern.pattern):
                        self.assertIsNone(pattern.search(source), "Possible secret in notebook")

    def test_dq_checks_use_documented_severities(self):
        """Every dq(...) call (positional or severity= keyword) uses BLOCK, REVIEW or LOG."""
        for path in NOTEBOOKS:
            for index, code in python_cells(load_notebook(path)):
                for line, check_id, severity in dq_calls(code):
                    if severity is None:
                        continue   # severity passed as a variable
                    with self.subTest(notebook=path.name, check=check_id, line=line):
                        self.assertIn(severity, ALLOWED_SEVERITIES)


if __name__ == "__main__":
    unittest.main()
