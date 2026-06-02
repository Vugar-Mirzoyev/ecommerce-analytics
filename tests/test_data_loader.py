"""Unit tests for the EcommerceDataLoader class."""

import os
import sqlite3
import tempfile

import pandas as pd
import pytest

# Ensure the project root is importable
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import EcommerceDataLoader


@pytest.fixture
def tmp_db(tmp_path):
    """Create a temporary SQLite database for testing."""
    db_path = str(tmp_path / "test.db")
    return db_path


@pytest.fixture
def loader(tmp_db):
    """Return a loader connected to a temporary database."""
    return EcommerceDataLoader(db_path=tmp_db)


@pytest.fixture
def csv_dir(tmp_path):
    """Create a temporary directory with a small sample CSV file."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    sample_df = pd.DataFrame({
        "order_id": ["o1", "o2", "o3"],
        "customer_id": ["c1", "c2", "c3"],
        "order_status": ["delivered", "delivered", "shipped"],
        "order_purchase_timestamp": ["2017-01-01", "2017-02-01", "2017-03-01"],
    })
    sample_df.to_csv(raw_dir / "olist_orders_dataset.csv", index=False)
    return str(raw_dir)


class TestEcommerceDataLoader:
    """Tests for EcommerceDataLoader."""

    def test_connection_established(self, loader):
        """Verify that the loader opens a valid database connection."""
        assert loader.conn is not None
        # Connection should be usable
        cursor = loader.conn.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1

    def test_load_raw_data_creates_table(self, tmp_db, csv_dir):
        """Verify that load_raw_data creates a table from CSV."""
        loader = EcommerceDataLoader(db_path=tmp_db)
        loader.load_raw_data(csv_dir=csv_dir)

        # The 'orders' table should exist and contain 3 rows
        result = loader.query("SELECT COUNT(*) AS cnt FROM orders")
        assert result["cnt"].iloc[0] == 3

    def test_load_raw_data_skips_missing_files(self, tmp_db, csv_dir, capsys):
        """Verify that missing CSV files are skipped without errors."""
        loader = EcommerceDataLoader(db_path=tmp_db)
        # Should not raise even though most CSVs are missing
        loader.load_raw_data(csv_dir=csv_dir)

    def test_query_returns_dataframe(self, loader):
        """Verify that query() returns a pandas DataFrame."""
        result = loader.query("SELECT 42 AS answer")
        assert isinstance(result, pd.DataFrame)
        assert result["answer"].iloc[0] == 42

    def test_close_connection(self, loader):
        """Verify that close() properly closes the database connection."""
        loader.close()
        with pytest.raises(Exception):
            loader.conn.execute("SELECT 1")
