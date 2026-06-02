import pandas as pd
import os


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
            DataFrame with RFM scores and customer segment labels.
        """
        sql = self._read_sql_file("rfm_analysis.sql")
        df = self.loader.query(sql)

        # Score each metric from 1 to 5
        df["R"] = pd.qcut(df["recency_days"], q=5, labels=[5, 4, 3, 2, 1])
        df["F"] = pd.qcut(df["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5])
        df["M"] = pd.qcut(df["monetary"], q=5, labels=[1, 2, 3, 4, 5])

        df["rfm_total"] = df["R"].astype(int) + df["F"].astype(int) + df["M"].astype(int)

        # Assign customer segments
        def segment(score):
            if score >= 13:
                return "Champions"
            elif score >= 10:
                return "Loyal Customers"
            elif score >= 7:
                return "Potential"
            else:
                return "Hibernating"

        df["segment"] = df["rfm_total"].apply(segment)
        return df

    def summary_metrics(self):
        """Compute high-level summary metrics for the dashboard.

        Returns:
            A pandas Series with: total_orders, total_revenue, total_customers, avg_rating.
        """
        sql = self._read_sql_file("summary_metrics.sql")
        return self.loader.query(sql).iloc[0]