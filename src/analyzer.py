import numpy as np
import os

from src.data_quality import run_checks


def _percentile_score(values, higher_is_better=True):
    """Score values from 1 to 5 by percentile rank.

    Tied values always get the same score, so the result does not depend on row order.

    Args:
        values: A numeric pandas Series.
        higher_is_better: If False, the lowest values get score 5.

    Returns:
        An integer Series with scores 1-5.
    """
    score = np.ceil(values.rank(pct=True, method="max") * 5).astype(int).clip(1, 5)
    return score if higher_is_better else 6 - score


def score_rfm(df):
    """Add RFM scores and a segment label to per-customer RFM values.

    About 97% of Olist customers ordered only once, so frequency quintiles cannot
    separate them. Frequency is therefore scored on fixed order counts, and customers
    are first split into repeat and one-time buyers, then by recency + monetary score.

    Args:
        df: DataFrame with columns recency_days, frequency, monetary.

    Returns:
        A copy of df with R, F, M, rfm_total and segment columns.
    """
    df = df.copy()
    df["R"] = _percentile_score(df["recency_days"], higher_is_better=False)
    df["F"] = np.select([df["frequency"] >= 3, df["frequency"] == 2], [5, 3], default=1)
    df["M"] = _percentile_score(df["monetary"])
    df["rfm_total"] = df["R"] + df["F"] + df["M"]

    repeat_buyer = df["frequency"] >= 2
    high_value = df["R"] + df["M"] >= 7
    df["segment"] = np.select(
        [repeat_buyer & high_value, repeat_buyer, high_value],
        ["Champions", "Loyal Customers", "Potential"],
        default="Hibernating",
    )
    return df


class SalesAnalyzer:
    """Provides analytical methods for e-commerce sales data."""

    # Directory where standalone SQL files are stored
    SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "sql")

    def __init__(self, loader):
        self.loader = loader

    def _read_sql_file(self, filename):
        """Read a SQL query from the sql/ directory.

        Args:
            filename: Name of the .sql file to read.

        Returns:
            The SQL query as a string.
        """
        filepath = os.path.join(self.SQL_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def monthly_revenue(self):
        """Calculate monthly revenue trend.

        Returns:
            DataFrame with columns: month, total_orders, revenue.
        """
        sql = self._read_sql_file("monthly_revenue.sql")
        return self.loader.query(sql)

    def top_categories(self):
        """Get top-selling product categories.

        Returns:
            DataFrame with columns: category, total_sold, total_revenue, avg_price.
        """
        sql = self._read_sql_file("top_categories.sql")
        return self.loader.query(sql)

    def rfm_segments(self):
        """Customer segmentation via RFM (Recency, Frequency, Monetary) analysis.

        Returns:
            DataFrame with one row per customer_unique_id, RFM scores and segment labels.
        """
        sql = self._read_sql_file("rfm_analysis.sql")
        return score_rfm(self.loader.query(sql))

    def data_quality(self):
        """Run the data quality checks the queries depend on.

        Returns:
            DataFrame with columns: check, rows, why.
        """
        return run_checks(self.loader)

    def summary_metrics(self):
        """Compute high-level summary metrics for the dashboard.

        Returns:
            A pandas Series with: total_orders, total_revenue, total_customers, avg_rating.
        """
        sql = self._read_sql_file("summary_metrics.sql")
        return self.loader.query(sql).iloc[0]