"""Unit tests for the data quality checks."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_quality import CHECKS, run_checks


class TestDataQuality:
    """Tests for run_checks."""

    def test_one_row_per_check(self, sample_loader):
        """Verify every check is reported with its explanation."""
        df = run_checks(sample_loader)
        assert list(df.columns) == ["check", "rows", "why"]
        assert len(df) == len(CHECKS)
        assert df["why"].str.len().gt(0).all()

    def test_counts_match_sample_data(self, sample_loader):
        """Verify each check finds exactly the traps planted in the sample data."""
        counts = run_checks(sample_loader).set_index("check")["rows"].to_dict()
        assert counts == {
            "Real customers with more than one customer_id": 1,
            "Orders with more than one payment row": 1,
            "Orders with more than one review": 1,
            "Delivered orders without a review": 1,
            "Delivered orders without a payment": 0,
            "Reviews linked to more than one order": 1,
            "Products without a category": 1,
            "Duplicate order_id rows": 0,
        }
