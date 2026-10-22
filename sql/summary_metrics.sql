-- Summary Metrics
-- Returns high-level KPIs for delivered orders: total orders, total revenue,
-- unique customers, average rating.
--
-- Each KPI is computed on its own table. Joining payments and reviews in one query
-- repeats an order once per payment and per review, and drops orders without a review.

WITH delivered AS (
    SELECT o.order_id, c.customer_unique_id
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
)
SELECT
    (SELECT COUNT(*) FROM delivered) AS total_orders,
    (SELECT ROUND(SUM(p.payment_value), 2)
       FROM payments p
       JOIN delivered d ON p.order_id = d.order_id) AS total_revenue,
    (SELECT COUNT(DISTINCT customer_unique_id) FROM delivered) AS total_customers,
    (SELECT ROUND(AVG(r.review_score), 2)
       FROM reviews r
       JOIN delivered d ON r.order_id = d.order_id) AS avg_rating;
