-- Summary Metrics
-- Returns high-level KPIs: total orders, total revenue, unique customers, average rating.

SELECT
    COUNT(DISTINCT o.order_id)     AS total_orders,
    ROUND(SUM(p.payment_value), 2) AS total_revenue,
    COUNT(DISTINCT o.customer_id)  AS total_customers,
    ROUND(AVG(r.review_score), 2)  AS avg_rating
FROM orders o
JOIN payments p ON o.order_id = p.order_id
JOIN reviews r  ON o.order_id = r.order_id
WHERE o.order_status = 'delivered';
