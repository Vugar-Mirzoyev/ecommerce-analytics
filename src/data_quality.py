"""Data quality checks behind the dashboard KPIs.

Each check counts the rows that break an assumption a query could easily make.
A non-zero count is not an error in the data, but the query has to handle it.

Run from the project root:  python -m src.data_quality
"""

import pandas as pd

CHECKS = [
    (
        "Real customers with more than one customer_id",
        """SELECT COUNT(*) FROM (
               SELECT customer_unique_id FROM customers
               GROUP BY customer_unique_id HAVING COUNT(*) > 1)""",
        "Olist issues a new customer_id for every order. Customers are counted "
        "by customer_unique_id.",
    ),
    (
        "Orders with more than one payment row",
        """SELECT COUNT(*) FROM (
               SELECT order_id FROM payments
               GROUP BY order_id HAVING COUNT(*) > 1)""",
        "A join to payments repeats the order. Payments are summed per order "
        "before joining.",
    ),
    (
        "Orders with more than one review",
        """SELECT COUNT(*) FROM (
               SELECT order_id FROM reviews
               GROUP BY order_id HAVING COUNT(*) > 1)""",
        "A join to reviews repeats the order and counts its revenue twice.",
    ),
    (
        "Delivered orders without a review",
        """SELECT COUNT(*) FROM orders
           WHERE order_status = 'delivered'
             AND order_id NOT IN (SELECT order_id FROM reviews)""",
        "An inner join to reviews drops these orders from revenue and order counts. "
        "Revenue is computed without reviews.",
    ),
    (
        "Delivered orders without a payment",
        """SELECT COUNT(*) FROM orders
           WHERE order_status = 'delivered'
             AND order_id NOT IN (SELECT order_id FROM payments)""",
        "Counted as an order, adds nothing to revenue.",
    ),
    (
        "Reviews linked to more than one order",
        """SELECT COUNT(*) FROM (
               SELECT review_id FROM reviews
               GROUP BY review_id HAVING COUNT(DISTINCT order_id) > 1)""",
        "review_id is not unique, so it is never used as a key.",
    ),
    (
        "Products without a category",
        "SELECT COUNT(*) FROM products WHERE product_category_name IS NULL",
        "Shown as 'Unknown' in the category ranking.",
    ),
    (
        "Duplicate order_id rows",
        "SELECT COUNT(*) - COUNT(DISTINCT order_id) FROM orders",
        "Must be 0: every order count assumes one row per order.",
    ),
]


def run_checks(loader):
    """Run every check against the database behind loader.

    Args:
        loader: An EcommerceDataLoader (or anything with a query(sql) method).

    Returns:
        DataFrame with columns: check, rows, why.
    """
    rows = []
    for name, sql, why in CHECKS:
        count = int(loader.query(sql).iloc[0, 0])
        rows.append({"check": name, "rows": count, "why": why})
    return pd.DataFrame(rows)


if __name__ == "__main__":
    from src.data_loader import EcommerceDataLoader

    loader = EcommerceDataLoader()
    with pd.option_context("display.max_colwidth", 80, "display.width", 160):
        print(run_checks(loader).to_string(index=False))
    loader.close()
