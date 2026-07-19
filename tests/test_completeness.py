from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from seismo.completeness import estimate_mc_maxc, monthly_moving_mc


class CompletenessTests(unittest.TestCase):
    def test_maxc_selects_most_frequent_bin(self) -> None:
        result = estimate_mc_maxc([1.0, 1.1, 1.1, 1.1, 1.2, 1.2], bin_width=0.1)
        self.assertEqual(result["mc"], 1.1)
        self.assertEqual(result["sample_count"], 6)

    def test_maxc_tie_selects_lower_bin(self) -> None:
        result = estimate_mc_maxc([1.0, 1.0, 1.1, 1.1], bin_width=0.1)
        self.assertEqual(result["mc"], 1.0)

    def test_monthly_three_month_windows(self) -> None:
        events = [
            {"time": "2026-01-10T00:00:00Z", "magnitude": 1.0},
            {"time": "2026-02-10T00:00:00Z", "magnitude": 1.1},
            {"time": "2026-03-10T00:00:00Z", "magnitude": 1.1},
            {"time": "2026-04-10T00:00:00Z", "magnitude": 1.2},
        ]
        results = monthly_moving_mc(events, window_months=3, minimum_samples=3)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["window_start"], "2026-01-01")
        self.assertEqual(results[0]["window_end"], "2026-03-01")
        self.assertEqual(results[0]["mc"], 1.1)
        self.assertEqual(results[0]["quality"], "ok")

    def test_invalid_bin_width(self) -> None:
        with self.assertRaises(ValueError):
            estimate_mc_maxc([1.0], bin_width=0)


if __name__ == "__main__":
    unittest.main()
