import unittest

import pandas as pd
from src.data_model import prepare_data, matched_year_change


class AnalysisTests(unittest.TestCase):
    def setUp(self):
        self.observations = pd.DataFrame({
            "Country Code": ["AAA", "AAA", "BBB", "WLD"],
            "Country Name": ["A", "A", "B", "World"],
            "Indicator Code": ["IS.AIR.PSGR"] * 4,
            "Year": [2020, 2021, 2021, 2021],
            "Value": [100, 150, 500, 650],
        })
        self.countries = pd.DataFrame({
            "Country Code": ["AAA", "BBB", "WLD"],
            "Region": ["Region", "Region", None],
            "IncomeGroup": ["High income", "Low income", None],
        })

    def test_aggregate_is_excluded_from_economy_totals(self):
        frame = prepare_data(self.observations, self.countries)
        current = frame.loc[~frame.is_aggregate & frame.Year.eq(2021)]
        self.assertEqual(current.Value.sum(), 650)

    def test_growth_uses_only_matched_economies(self):
        frame = prepare_data(self.observations, self.countries)
        change, count = matched_year_change(frame.loc[~frame.is_aggregate], 2021)
        self.assertAlmostEqual(change, 50)
        self.assertEqual(count, 1)

    def test_duplicates_fail_instead_of_inflating_totals(self):
        duplicated = pd.concat([self.observations, self.observations.iloc[:1]])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            prepare_data(duplicated, self.countries)

    def test_missing_baseline_does_not_invent_a_change(self):
        frame = prepare_data(self.observations, self.countries)
        change, count = matched_year_change(frame, 2020)
        self.assertIsNone(change)
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
