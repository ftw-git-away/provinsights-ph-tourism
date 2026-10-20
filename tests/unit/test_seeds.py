"""Data checks on the reviewed seed files in resources/seeds (rules from resources/seeds/README.md)."""
import re
import unittest

from _helpers import SEEDS, read_csv

PSGC = re.compile(r"^\d{10}$")

SEED_RULES = {
    "map_dot_area_to_psgc.csv": {
        "rows": 161,
        "key": ("dot_indent_level", "dot_parent_label", "dot_area_label", "valid_from_year"),
        "row_roles": {"province_unit", "add_to_parent", "exclude", "region_total", "national_total"},
        "code_columns": ("unit_psgc_code", "area_psgc_code"),
    },
    "map_psa_area_to_psgc.csv": {
        "rows": 134,
        "key": ("psa_label",),
        "row_roles": {"unit", "add_to_unit", "ncr_component", "region_total"},
        "code_columns": ("psa_region_code", "unit_psgc_code", "area_psgc_code"),
    },
    "map_psa_population_area_to_psgc.csv": {
        "rows": 218,
        "key": ("source_table", "block_label", "area_label"),
        "row_roles": {"unit", "not_a_unit", "region_total", "national_total", "check_total", "huc"},
        "code_columns": ("unit_psgc_code", "from_unit_psgc_code", "area_psgc_code"),
    },
}
UNIT_ROLES = {"province_unit", "add_to_parent", "unit", "add_to_unit", "check_total", "huc"}
REPORTING_UNITS = 100


class SeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        header, rows = read_csv(SEEDS / "map_unit_coordinates.csv")
        cls.coordinates = rows
        cls.units = {row["province_psgc"] for row in rows}

    def test_label_maps_have_expected_rows_roles_and_unique_keys(self):
        for name, rule in SEED_RULES.items():
            header, rows = read_csv(SEEDS / name)
            with self.subTest(seed=name, check="columns"):
                for column in (*rule["key"], "row_role", *rule["code_columns"], "notes"):
                    self.assertIn(column, header)
            with self.subTest(seed=name, check="row count"):
                self.assertEqual(len(rows), rule["rows"],
                                 "Row count changed: update the README table and this test together")
            with self.subTest(seed=name, check="unique key"):
                keys = [tuple(row[c] for c in rule["key"]) for row in rows]
                duplicates = {k for k in keys if keys.count(k) > 1}
                self.assertFalse(duplicates, f"Duplicate keys: {sorted(duplicates)[:5]}")
            with self.subTest(seed=name, check="row_role"):
                unknown = {row["row_role"] for row in rows} - rule["row_roles"]
                self.assertFalse(unknown, f"Unknown row_role values: {unknown}")

    def test_psgc_codes_are_ten_digits(self):
        for name, rule in SEED_RULES.items():
            _, rows = read_csv(SEEDS / name)
            for number, row in enumerate(rows, start=2):
                for column in rule["code_columns"]:
                    value = row[column].strip()
                    if value:
                        with self.subTest(seed=name, line=number, column=column):
                            self.assertRegex(value, PSGC)

    def test_unit_codes_are_known_reporting_units(self):
        """Every row that loads a value into a unit points to one of the 100 reporting units."""
        for name in SEED_RULES:
            _, rows = read_csv(SEEDS / name)
            for number, row in enumerate(rows, start=2):
                code = row["unit_psgc_code"].strip()
                if row["row_role"] in UNIT_ROLES and code:
                    with self.subTest(seed=name, line=number):
                        self.assertIn(code, self.units)

    def test_coordinates_cover_every_unit_once(self):
        self.assertEqual(len(self.coordinates), REPORTING_UNITS)
        self.assertEqual(len(self.units), REPORTING_UNITS, "Duplicate province_psgc in coordinates")
        for row in self.coordinates:
            with self.subTest(unit=row["province_psgc"]):
                self.assertRegex(row["province_psgc"], PSGC)
                self.assertTrue(4.0 <= float(row["latitude"]) <= 21.5, "Latitude outside the Philippines")
                self.assertTrue(116.0 <= float(row["longitude"]) <= 127.0, "Longitude outside the Philippines")

    def test_dot_validity_periods_are_ordered(self):
        _, rows = read_csv(SEEDS / "map_dot_area_to_psgc.csv")
        for number, row in enumerate(rows, start=2):
            start, end = row["valid_from_year"], row["valid_to_year"]
            with self.subTest(line=number):
                self.assertRegex(start, r"^\d{4}$")
                if end:
                    self.assertLessEqual(int(start), int(end))


if __name__ == "__main__":
    unittest.main()
