-- RFM Analysis — Customer Segmentation
-- Returns per-customer recency (days since last order), frequency, and monetary value.
-- Python code applies scoring and segment labeling on top of these results.
--
-- One row per real customer: Olist issues a new customer_id for every order, so the
-- customer is customer_unique_id. Payments are summed per order before the join, so
-- an order paid in several parts still counts as one order. Recency is measured from
-- the last purchase in the data, not from today.

WITH delivered AS (
    SELECT
        o.order_id,
        c.customer_unique_id,
        o.order_purchase_timestamp
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
),
order_value AS (
    SELECT order_id, SUM(payment_value) AS order_value
    FROM payments
    GROUP BY order_id
),
reference AS (
    SELECT MAX(order_purchase_timestamp) AS reference_date
    FROM delivered
)
SELECT
    d.customer_unique_id,
    CAST(julianday(r.reference_date) - julianday(MAX(d.order_purchase_timestamp)) AS INTEGER) AS recency_days,
    COUNT(DISTINCT d.order_id)                AS frequency,
    ROUND(COALESCE(SUM(v.order_value), 0), 2) AS monetary
FROM delivered d
LEFT JOIN order_value v ON d.order_id = v.order_id
CROSS JOIN reference r
GROUP BY d.customer_unique_id;
