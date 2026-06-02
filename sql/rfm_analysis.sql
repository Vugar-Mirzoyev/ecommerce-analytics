-- RFM Analysis — Customer Segmentation
-- Returns per-customer recency (days since last order), frequency, and monetary value.
-- Python code applies quantile scoring and segment labeling on top of these results.

SELECT
    o.customer_id,
    CAST(julianday('now') - julianday(MAX(o.order_purchase_timestamp)) AS INTEGER) AS recency_days,
    COUNT(o.order_id)              AS frequency,
    ROUND(SUM(p.payment_value), 2) AS monetary
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY o.customer_id;
