-- Episode 5: headline numbers (DuckDB)
-- Only customers whose first order was Oct 2025 to Jun 2026 are judged,
-- so every one of them had a full 3 months to come back.
WITH first_order AS (
    SELECT customer_id, MIN(order_date) AS first_date
    FROM orders GROUP BY customer_id
),
mature AS (
    SELECT * FROM first_order WHERE first_date < DATE '2026-07-01'
),
back_in_3 AS (
    SELECT m.customer_id,
           MAX(CASE WHEN o.order_date > m.first_date
                     AND DATE_TRUNC('month', o.order_date)
                         <= DATE_TRUNC('month', m.first_date) + INTERVAL 3 MONTH
                    THEN 1 ELSE 0 END) AS came_back
    FROM mature m
    JOIN orders o USING (customer_id)
    GROUP BY m.customer_id
)
SELECT COUNT(*)                                  AS customers,
       SUM(came_back)                            AS came_back,
       ROUND(100.0 * (1 - AVG(came_back)), 1)    AS never_back_pct
FROM back_in_3;
