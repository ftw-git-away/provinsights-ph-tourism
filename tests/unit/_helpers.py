"""Shared helpers for the unit tests. Standard library only, except sqlglot and PyYAML."""
import ast
import csv
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOKS = sorted((REPO_ROOT / "notebooks").rglob("*.ipynb"))
JOB_FILE = REPO_ROOT / "resources" / "jobs" / "tourism_pipeline.yml"
SEEDS = REPO_ROOT / "resources" / "seeds"

MAGIC_LINE = re.compile(r"^\s*[%!][A-Za-z]")   # %pip, %sql, !ls ... but not "!=" inside code


def cell_source(cell):
    source = cell.get("source", "")
    return "".join(source) if isinstance(source, list) else source


def load_notebook(path):
    return json.loads(path.read_text(encoding="utf-8"))


def first_magic(source):
    """Return 'python', 'sql', 'md', 'pip', ... for a cell's first magic line, or None."""
    for line in source.splitlines():
        if line.strip():
            match = re.match(r"^\s*%(\w+)", line)
            return match.group(1).lower() if match else None
    return None


def python_cells(notebook):
    """Yield (index, code) for every Python code cell, with magic and shell lines blanked out.

    Notebooks without a magic are Python by default (the Databricks notebook language here).
    """
    for index, cell in enumerate(notebook["cells"], start=1):
        if cell.get("cell_type") != "code":
            continue
        source = cell_source(cell)
        magic = first_magic(source)
        if magic not in (None, "python", "pip"):
            continue
        code = "\n".join("" if MAGIC_LINE.match(line) else line for line in source.splitlines())
        yield index, code


def sql_cells(notebook):
    """Yield (index, sql) for every %sql cell, without the magic line."""
    for index, cell in enumerate(notebook["cells"], start=1):
        if cell.get("cell_type") != "code":
            continue
        source = cell_source(cell)
        if first_magic(source) == "sql":
            lines = source.splitlines()
            start = next(i for i, line in enumerate(lines) if line.strip())
            yield index, "\n".join(lines[start + 1:])


def spark_sql_strings(code):
    """Yield (line, sql) for every spark.sql("...") call whose SQL is a plain or f-string literal.

    f-string placeholders such as {CATALOG} are replaced with a dummy identifier so the SQL can be parsed.
    """
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "sql" and node.args):
            continue
        arg = node.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            yield node.lineno, arg.value
        elif isinstance(arg, ast.JoinedStr):
            parts = []
            for value in arg.values:
                if isinstance(value, ast.Constant):
                    parts.append(str(value.value))
                else:
                    parts.append("placeholder")
            yield node.lineno, "".join(parts)


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames, list(reader)
