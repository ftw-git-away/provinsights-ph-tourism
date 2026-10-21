"""SQL checks: every %sql cell and every spark.sql("...") literal must be valid Databricks SQL.

spark.sql(variable) calls are not checked: the SQL is only known at run time.
"""
import logging
import re
import unittest

import sqlglot
from sqlglot import errors as sqlglot_errors
from sqlglot import exp

from _helpers import NOTEBOOKS, load_notebook, python_cells, spark_sql_strings, sql_cells

logging.getLogger("sqlglot").setLevel(logging.ERROR)   # unsupported statements are checked below instead

# Statements sqlglot does not model and keeps as an unparsed Command. Anything else that falls back fails.
ALLOWED_UNPARSED = {"SHOW"}


def check_sql(testcase, sql, where):
    sql = re.sub(r"\$\{[^}]+\}|:\w+", "placeholder", sql)   # widget / parameter markers
    try:
        statements = sqlglot.parse(sql, read="databricks")
    except sqlglot_errors.SqlglotError as exc:
        testcase.fail(f"{where}: {exc}")
    for statement in statements:
        if isinstance(statement, exp.Command):
            testcase.assertIn(str(statement.this).upper(), ALLOWED_UNPARSED,
                              f"{where}: sqlglot could not parse this statement: {str(statement)[:120]}")


class NotebookSqlTests(unittest.TestCase):
    def test_sql_cells_parse(self):
        for path in NOTEBOOKS:
            for index, sql in sql_cells(load_notebook(path)):
                with self.subTest(notebook=path.name, cell=index):
                    self.assertTrue(sql.strip(), "Empty %sql cell")
                    check_sql(self, sql, f"{path.name} cell {index}")

    def test_spark_sql_strings_parse(self):
        for path in NOTEBOOKS:
            for index, code in python_cells(load_notebook(path)):
                for line, sql in spark_sql_strings(code):
                    with self.subTest(notebook=path.name, cell=index, line=line):
                        check_sql(self, sql, f"{path.name} cell {index} line {line}")


if __name__ == "__main__":
    unittest.main()
