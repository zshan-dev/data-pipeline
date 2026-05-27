import os
import sys
import unittest


SRC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from risk_engine import (  # noqa: E402
    compute_weighted_sentiment_score,
    simulate_funded_status,
)


class RiskEnginePureMathTests(unittest.TestCase):
    def test_weighted_sentiment_missing_assets_treated_as_zero(self):
        sentiment = {"Equities": 1.0}
        weights = {"Equities": 0.38, "Real Estate": 0.18}
        score = compute_weighted_sentiment_score(sentiment, weights)
        # weighted_sum = 1.0*0.38 + 0.0*0.18 = 0.38; total_weight=0.56 => 0.67857...
        self.assertAlmostEqual(score, 0.38 / 0.56, places=6)

    def test_simulate_funded_status_applies_clamped_shock(self):
        prior_assets = 100.0
        prior_liabilities = 90.0

        # raw_shock = 10 * 0.02 = 0.2, but clamp to max_shock_pct=0.02
        result = simulate_funded_status(
            prior_assets,
            prior_liabilities,
            weighted_sentiment_score=10.0,
            sensitivity=0.02,
            max_shock_pct=0.02,
        )
        self.assertAlmostEqual(result.shock_pct, 0.02, places=8)
        self.assertAlmostEqual(result.total_assets, 102.0, places=8)
        self.assertAlmostEqual(result.funded_ratio, 102.0 / 90.0, places=8)

    def test_simulate_funded_status_no_clamp_with_reasonable_score(self):
        prior_assets = 100.0
        prior_liabilities = 80.0

        # raw_shock = (-0.5)*0.02 = -0.01 (within clamp)
        result = simulate_funded_status(
            prior_assets,
            prior_liabilities,
            weighted_sentiment_score=-0.5,
            sensitivity=0.02,
            max_shock_pct=0.02,
        )
        self.assertAlmostEqual(result.shock_pct, -0.01, places=8)
        self.assertAlmostEqual(result.total_assets, 99.0, places=8)
        self.assertAlmostEqual(result.funded_ratio, 99.0 / 80.0, places=8)


if __name__ == "__main__":
    unittest.main()

