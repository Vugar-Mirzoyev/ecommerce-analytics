-- Monthly Revenue Trend
-- Returns aggregated monthly order counts and revenue for delivered orders.

SELECT
    substr(o.order_purchase_timestamp, 1, 7) AS month,
    COUNT(DISTINCT o.order_id)                AS total_orders,
    ROUND(SUM(p.payment_value), 2)            AS revenue
FROM orders o
JOIN payments p ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month;
