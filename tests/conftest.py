"""Shared sample database for the analyzer and data quality tests.

The data carries the same traps as the real Olist tables, so the tests fail if a
query handles them wrong:
- customers c1, c2 and c3 are the same person (u1), with one order each;
- order o5 is paid in two parts;
- order o3 has two reviews, and review r10 is linked to both o10 and o11;
- delivered order o20 has no review;
- order o21 is canceled and must not count anywhere;
- product p6 has no category.
"""

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import EcommerceDataLoader

REVIEW_SCORES = [4, 5, 3, 4, 5, 2, 4, 3, 5, 4, 3, 5, 4, 2, 5, 3, 4, 5, 4]  # o1..o19
SECOND_REVIEW_O3 = 1


@pytest.fixture
def sample_loader(tmp_path):
    """Return a loader backed by a temporary database with sample data."""
    loader = EcommerceDataLoader(db_path=str(tmp_path / "test.db"))
    conn = loader.conn

    orders_df = pd.DataFrame({
        "order_id": [f"o{i}" for i in range(1, 22)],
        "customer_id": [f"c{i}" for i in range(1, 22)],
        "order_status": ["delivered"] * 20 + ["canceled"],
        "order_purchase_timestamp": [
            f"2017-{str(m).zfill(2)}-15 10:00:00" for m in range(1, 13)
        ] + [
            f"2018-{str(m).zfill(2)}-15 10:00:00" for m in range(1, 9)
        ] + ["2018-08-20 10:00:00"],
    })
    orders_df.to_sql("orders", conn, if_exists="replace", index=False)

    customers_df = pd.DataFrame({
        "customer_id": [f"c{i}" for i in range(1, 22)],
        "customer_unique_id": ["u1", "u1", "u1"] + [f"u{i}" for i in range(4, 22)],
    })
    customers_df.to_sql("customers", conn, if_exists="replace", index=False)

    payments_df = pd.DataFrame({
        "order_id": [f"o{i}" for i in range(1, 21)] + ["o5", "o21"],
        "payment_value": [100.0 + i * 10 for i in range(20)] + [50.0, 999.0],
    })
    payments_df.to_sql("payments", conn, if_exists="replace", index=False)

    items_df = pd.DataFrame({
        "order_id": [f"o{i}" for i in range(1, 22)],
        "product_id": [f"p{i % 5 + 1}" for i in range(20)] + ["p1"],
        "price": [50.0 + i * 5 for i in range(20)] + [10000.0],
    })
    items_df.to_sql("items", conn, if_exists="replace", index=False)

    products_df = pd.DataFrame({
        "product_id": [f"p{i}" for i in range(1, 7)],
        "product_category_name": ["electronics", "clothing", "books", "toys", "sports", None],
    })
    products_df.to_sql("products", conn, if_exists="replace", index=False)

    reviews_df = pd.DataFrame({
        "review_id": [f"r{i}" for i in range(1, 11)] + ["r10"]
                     + [f"r{i}" for i in range(12, 20)] + ["r3b"],
        "order_id": [f"o{i}" for i in range(1, 20)] + ["o3"],
        "review_score": REVIEW_SCORES + [SECOND_REVIEW_O3],
    })
    reviews_df.to_sql("reviews", conn, if_exists="replace", index=False)

    yield loader
    loader.close()
