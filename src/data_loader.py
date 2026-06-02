import pandas as pd
import sqlite3
import os
import logging

logger = logging.getLogger(__name__)


class EcommerceDataLoader:
    """Loads CSV datasets into a SQLite database and provides a query interface."""

    def __init__(self, db_path="data/ecommerce.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        logger.info("Database connection established")

    def load_raw_data(self, csv_dir="data/raw"):
        """Load CSV files into the SQLite database.

        Args:
            csv_dir: Path to the directory containing raw CSV files.
        """
        files = {
            "orders":    "olist_orders_dataset.csv",
            "items":     "olist_order_items_dataset.csv",
            "products":  "olist_products_dataset.csv",
            "customers": "olist_customers_dataset.csv",
            "payments":  "olist_order_payments_dataset.csv",
            "reviews":   "olist_order_reviews_dataset.csv",
        }

        for table_name, file_name in files.items():
            file_path = os.path.join(csv_dir, file_name)

            if not os.path.exists(file_path):
                logger.warning("File not found: %s", file_path)
                continue

            df = pd.read_csv(file_path)
            df.to_sql(table_name, self.conn, if_exists="replace", index=False)
            logger.info("%s table loaded — %s rows", table_name, f"{len(df):,}")

        logger.info("All data loaded successfully!")

    def query(self, sql):
        """Execute a SQL query and return results as a DataFrame.

        Args:
            sql: A valid SQL query string.

        Returns:
            A pandas DataFrame containing the query results.
        """
        return pd.read_sql_query(sql, self.conn)

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")