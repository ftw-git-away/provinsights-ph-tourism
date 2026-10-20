"""SQL checks: every %sql cell and every spark.sql("...") string must be valid Databricks SQL."""
import logging
import re
import unittest

import sqlglot
from sqlglot import errors as sqlglot_errors

from _helpers import NOTEBOOKS, load_notebook, python_cells, spark_sql_strings, sql_cells



logging.getLogger("sqlglot").setLevel(logging.ERROR)   # hide "falling back to Command" notes


def parse(sql):
    sql = re.sub(r"\$\{[^}]+\}|:\w+", "placeholder", sql)   # widget / parameter markers
    sqlglot.parse(sql, read="databricks")


class NotebookSqlTests(unittest.TestCase):
    def test_sql_cells_parse(self):
        for path in NOTEBOOKS:
            for index, sql in sql_cells(load_notebook(path)):
                with self.subTest(notebook=path.name, cell=index):
                    self.assertTrue(sql.strip(), "Empty %sql cell")
                    try:
                        parse(sql)
                    except sqlglot_errors.SqlglotError as exc:
                        self.fail(f"{path.name} cell {index}: {exc}")

    def test_spark_sql_strings_parse(self):
        for path in NOTEBOOKS:
            for index, code in python_cells(load_notebook(path)):
                for line, sql in spark_sql_strings(code):
                    with self.subTest(notebook=path.name, cell=index, line=line):
                        try:
                            parse(sql)
                        except sqlglot_errors.SqlglotError as exc:
                            self.fail(f"{path.name} cell {index} line {line}: {exc}")


if __name__ == "__main__":
    unittest.main()
