-- Episode 5: who brings the revenue? Repeat = a customer with 2+ orders in the window (DuckDB)
WITH per_customer AS (
    SELECT c.customer_id, c.customer_type,
           COUNT(*) AS orders, SUM(o.order_value) AS revenue
    FROM orders o JOIN customers c USING (customer_id)
    GROUP BY c.customer_id, c.customer_type
)
SELECT customer_type,
       COUNT(*)                                             AS customers,
       ROUND(100.0 * SUM(CASE WHEN orders > 1 THEN 1 END) / COUNT(*), 1) AS repeat_pct,
       SUM(revenue)                                         AS revenue,
       ROUND(100.0 * SUM(revenue) / SUM(SUM(revenue)) OVER (), 1) AS revenue_share_pct
FROM per_customer
GROUP BY customer_type
ORDER BY revenue DESC;
