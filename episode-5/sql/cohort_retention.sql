-- Episode 5: monthly repeat-purchase cohorts (DuckDB)
-- Cohort = the month a customer placed their FIRST order.
-- month_n = how many calendar months later they ordered again (0 = first month).
WITH first_order AS (
    SELECT customer_id,
           DATE_TRUNC('month', MIN(order_date)) AS cohort_month
    FROM orders
    GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT
           o.customer_id,
           f.cohort_month,
           DATE_DIFF('month', f.cohort_month, DATE_TRUNC('month', o.order_date)) AS month_n
    FROM orders o
    JOIN first_order f USING (customer_id)
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) AS customers
    FROM first_order
    GROUP BY cohort_month
)
SELECT a.cohort_month,
       s.customers,
       a.month_n,
       COUNT(*) AS active_customers,
       ROUND(100.0 * COUNT(*) / s.customers, 1) AS retention_pct
FROM activity a
JOIN cohort_size s USING (cohort_month)
GROUP BY a.cohort_month, s.customers, a.month_n
ORDER BY a.cohort_month, a.month_n;
