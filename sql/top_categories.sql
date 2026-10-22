-- Top-Selling Product Categories
-- Returns the top 10 categories ranked by total revenue (item price, without freight).
-- Delivered orders only, like every other KPI on the dashboard.

SELECT
    COALESCE(p.product_category_name, 'Unknown') AS category,
    COUNT(*)                                      AS total_sold,
    ROUND(SUM(i.price), 2)                        AS total_revenue,
    ROUND(AVG(i.price), 2)                        AS avg_price
FROM items i
JOIN orders o   ON i.order_id = o.order_id
JOIN products p ON i.product_id = p.product_id
WHERE o.order_status = 'delivered'
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;
