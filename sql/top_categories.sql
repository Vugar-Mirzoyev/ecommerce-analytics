-- Top-Selling Product Categories
-- Returns the top 10 categories ranked by total revenue.

SELECT
    COALESCE(p.product_category_name, 'Unknown') AS category,
    COUNT(*)                                      AS total_sold,
    ROUND(SUM(i.price), 2)                        AS total_revenue,
    ROUND(AVG(i.price), 2)                        AS avg_price
FROM items i
JOIN products p ON i.product_id = p.product_id
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 10;
