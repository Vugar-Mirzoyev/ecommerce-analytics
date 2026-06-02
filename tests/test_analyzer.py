"""Unit tests for the SalesAnalyzer class."""

import os
import sqlite3
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import EcommerceDataLoader
from src.analyzer import SalesAnalyzer


@pytest.fixture
def analyzer(tmp_path):
    """Create an analyzer backed by an in-memory database with sample data."""
    db_path = str(tmp_path / "test.db")
    loader = EcommerceDataLoader(db_path=db_path)
    conn = loader.conn

    # Create sample tables
    orders_df = pd.DataFrame({
        "order_id": [f"o{i}" for i in range(1, 21)],
        "customer_id": [f"c{i}" for i in range(1, 21)],
        "order_status": ["delivered"] * 20,
        "order_purchase_timestamp": [
            f"2017-{str(m).zfill(2)}-15 10:00:00" for m in range(1, 13)
        ] + [
            f"2018-{str(m).zfill(2)}-15 10:00:00" for m in range(1, 9)
        ],
    })
    orders_df.to_sql("orders", conn, if_exists="replace", index=False)

    payments_df = pd.DataFrame({
        "order_id": [f"o{i}" for i in range(1, 21)],
        "payment_value": [100.0 + i * 10 for i in range(20)],
    })
    payments_df.to_sql("payments", conn, if_exists="replace", index=False)

    items_df = pd.DataFrame({
        "order_id": [f"o{i}" for i in range(1, 21)],
        "product_id": [f"p{i % 5 + 1}" for i in range(20)],
        "price": [50.0 + i * 5 for i in range(20)],
    })
    items_df.to_sql("items", conn, if_exists="replace", index=False)

    products_df = pd.DataFrame({
        "product_id": [f"p{i}" for i in range(1, 6)],
        "product_category_name": ["electronics", "clothing", "books", "toys", "sports"],
    })
    products_df.to_sql("products", conn, if_exists="replace", index=False)

    reviews_df = pd.DataFrame({
        "order_id": [f"o{i}" for i in range(1, 21)],
        "review_score": [4, 5, 3, 4, 5, 2, 4, 3, 5, 4, 3, 5, 4, 2, 5, 3, 4, 5, 4, 3],
    })
    reviews_df.to_sql("reviews", conn, if_exists="replace", index=False)

    return SalesAnalyzer(loader)


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
