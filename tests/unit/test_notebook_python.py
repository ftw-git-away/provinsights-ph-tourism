"""Python checks on every notebook: structure, syntax and shared conventions."""
import ast
import re
import unittest

from _helpers import NOTEBOOKS, cell_source, load_notebook, python_cells

ALLOWED_CATALOG = "tuklas_dev"
ALLOWED_SEVERITIES = {"BLOCK", "REVIEW", "LOG"}   # docs/data-quality-rules.md
SECRET_PATTERNS = [
    re.compile(r"dapi[0-9a-f]{32}"),                       # Databricks personal access token
    re.compile(r"ghp_[A-Za-z0-9]{36}"),                    # GitHub token
    re.compile(r"(?i)(password|secret|token)\s*=\s*['\"][^'\"]{8,}['\"]"),
]


class NotebookPythonTests(unittest.TestCase):
    def test_notebooks_exist(self):
        self.assertTrue(NOTEBOOKS, "No notebooks found under notebooks/")

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

    def test_dq_helper_records_known_severities(self):
        """Notebooks that define dq(...) must use a severity from docs/data-quality-rules.md."""
        for path in NOTEBOOKS:
            notebook = load_notebook(path)
            for index, code in python_cells(notebook):
                for node in ast.walk(ast.parse(code)):
                    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                            and node.func.id == "dq" and len(node.args) >= 3
                            and isinstance(node.args[2], ast.Constant)):
                        with self.subTest(notebook=path.name, cell=index, line=node.lineno):
                            self.assertIn(node.args[2].value, ALLOWED_SEVERITIES)


if __name__ == "__main__":
    unittest.main()
