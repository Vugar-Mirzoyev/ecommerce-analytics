"""Unit tests for the SalesAnalyzer class."""

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.analyzer import SalesAnalyzer, score_rfm
from tests.conftest import REVIEW_SCORES, SECOND_REVIEW_O3


@pytest.fixture
def analyzer(sample_loader):
    """Create an analyzer backed by the shared sample database."""
    return SalesAnalyzer(sample_loader)


class TestSalesAnalyzer:
    """Tests for SalesAnalyzer."""

    def test_monthly_revenue_columns(self, analyzer):
        """Verify monthly_revenue returns the expected columns."""
        df = analyzer.monthly_revenue()
        assert list(df.columns) == ["month", "total_orders", "revenue"]

    def test_monthly_revenue_has_data(self, analyzer):
        """Verify monthly_revenue returns rows."""
        df = analyzer.monthly_revenue()
        assert len(df) > 0

    def test_top_categories_max_10(self, analyzer):
        """Verify top_categories returns at most 10 rows."""
        df = analyzer.top_categories()
        assert len(df) <= 10

    def test_top_categories_columns(self, analyzer):
        """Verify top_categories returns the expected columns."""
        df = analyzer.top_categories()
        expected = ["category", "total_sold", "total_revenue", "avg_price"]
        assert list(df.columns) == expected

    def test_top_categories_delivered_only(self, analyzer):
        """Verify the canceled order's item is not counted in any category."""
        df = analyzer.top_categories()
        assert df["total_sold"].sum() == 20
        assert df["total_revenue"].max() < 10000

    def test_rfm_segments_columns(self, analyzer):
        """Verify rfm_segments returns RFM scoring columns."""
        df = analyzer.rfm_segments()
        for col in ["R", "F", "M", "rfm_total", "segment"]:
            assert col in df.columns

    def test_rfm_segments_labels(self, analyzer):
        """Verify rfm_segments assigns valid segment labels."""
        df = analyzer.rfm_segments()
        valid_segments = {
            "Champions",
            "Loyal Customers",
            "Potential",
            "Hibernating",
        }
        assert set(df["segment"].unique()).issubset(valid_segments)

    def test_rfm_one_row_per_real_customer(self, analyzer):
        """Verify three customer_ids of the same person become one customer with 3 orders."""
        df = analyzer.rfm_segments().set_index("customer_unique_id")
        assert len(df) == 18
        assert df.loc["u1", "frequency"] == 3
        assert df.loc["u1", "monetary"] == pytest.approx(330.0)

    def test_rfm_frequency_counts_orders_not_payments(self, analyzer):
        """Verify an order paid in two parts is one order with the full value."""
        df = analyzer.rfm_segments().set_index("customer_unique_id")
        assert df.loc["u5", "frequency"] == 1
        assert df.loc["u5", "monetary"] == pytest.approx(190.0)

    def test_rfm_recency_from_last_delivered_purchase(self, analyzer):
        """Verify recency is counted from the last delivered purchase, not from today."""
        df = analyzer.rfm_segments().set_index("customer_unique_id")
        assert df.loc["u20", "recency_days"] == 0
        assert df["recency_days"].max() < 600

    def test_one_time_buyers_never_champions_or_loyal(self, analyzer):
        """Verify only repeat buyers can be Champions or Loyal Customers."""
        df = analyzer.rfm_segments()
        one_time_segments = df.loc[df["frequency"] == 1, "segment"]
        assert not one_time_segments.isin(["Champions", "Loyal Customers"]).any()
        assert df.set_index("customer_unique_id").loc["u1", "segment"] in {
            "Champions", "Loyal Customers",
        }

    def test_summary_metrics_keys(self, analyzer):
        """Verify summary_metrics returns all 4 expected KPIs."""
        metrics = analyzer.summary_metrics()
        for key in ["total_orders", "total_revenue", "total_customers", "avg_rating"]:
            assert key in metrics.index

    def test_summary_metrics_positive(self, analyzer):
        """Verify summary metrics are positive numbers."""
        metrics = analyzer.summary_metrics()
        assert metrics["total_orders"] > 0
        assert metrics["total_revenue"] > 0
        assert metrics["total_customers"] > 0
        assert metrics["avg_rating"] > 0

    def test_summary_metrics_counts_orders_without_review(self, analyzer):
        """Verify all 20 delivered orders count, including o20 that has no review."""
        assert analyzer.summary_metrics()["total_orders"] == 20

    def test_summary_metrics_revenue_counts_each_payment_once(self, analyzer):
        """Verify revenue is not repeated by multiple payments or reviews of one order."""
        expected = sum(100.0 + i * 10 for i in range(20)) + 50.0
        assert analyzer.summary_metrics()["total_revenue"] == pytest.approx(expected)

    def test_summary_metrics_counts_real_customers(self, analyzer):
        """Verify customers are counted by customer_unique_id."""
        assert analyzer.summary_metrics()["total_customers"] == 18

    def test_summary_metrics_avg_rating_counts_each_review_once(self, analyzer):
        """Verify the average rating is not weighted by payment rows."""
        scores = REVIEW_SCORES + [SECOND_REVIEW_O3]
        expected = round(sum(scores) / len(scores), 2)
        assert analyzer.summary_metrics()["avg_rating"] == pytest.approx(expected)


class TestScoreRfm:
    """Tests for the RFM scoring function."""

    @pytest.fixture
    def rfm_values(self):
        rng = np.random.default_rng(42)
        n = 200
        return pd.DataFrame({
            "customer_unique_id": [f"u{i}" for i in range(n)],
            "recency_days": rng.integers(0, 50, n),
            "frequency": rng.choice([1, 1, 1, 1, 1, 1, 1, 1, 2, 3], n),
            "monetary": rng.integers(1, 20, n) * 10.0,
        })

    def test_segments_do_not_depend_on_row_order(self, rfm_values):
        """Verify shuffling the rows never changes a customer's scores or segment."""
        base = score_rfm(rfm_values).set_index("customer_unique_id")
        for seed in range(5):
            shuffled = rfm_values.sample(frac=1, random_state=seed)
            other = score_rfm(shuffled).set_index("customer_unique_id").loc[base.index]
            pd.testing.assert_frame_equal(other, base)

    def test_scores_are_between_1_and_5(self, rfm_values):
        """Verify R, F and M scores stay on the 1-5 scale."""
        df = score_rfm(rfm_values)
        for col in ["R", "F", "M"]:
            assert df[col].between(1, 5).all()

    def test_recent_customers_score_higher(self, rfm_values):
        """Verify a lower recency_days never gets a lower R score."""
        df = score_rfm(rfm_values).sort_values("recency_days")
        assert df["R"].is_monotonic_decreasing
