-- Episode 7: RFM scores and segments, one row per customer (DuckDB)
-- As-of date = 1 Oct 2026, the day after the last order in the data.
-- R and F use fixed business bands. M uses quintiles (NTILE), because rupee totals are almost all different.
-- NTILE on frequency would split customers with the SAME order count into different scores.
WITH rfm AS (
    SELECT customer_id,
           DATE_DIFF('day', MAX(order_date), DATE '2026-10-01') AS recency_days,
           COUNT(*)                                             AS frequency,
           SUM(order_value)                                     AS monetary
    FROM orders
    GROUP BY customer_id
),
scored AS (
    SELECT *,
           CASE WHEN recency_days <= 30  THEN 5
                WHEN recency_days <= 60  THEN 4
                WHEN recency_days <= 90  THEN 3
                WHEN recency_days <= 180 THEN 2
                ELSE 1 END                                      AS r_score,
           CASE WHEN frequency >= 8 THEN 5
                WHEN frequency >= 5 THEN 4
                WHEN frequency >= 3 THEN 3
                WHEN frequency = 2  THEN 2
                ELSE 1 END                                      AS f_score,
           NTILE(5) OVER (ORDER BY monetary, customer_id)       AS m_score
    FROM rfm
)
SELECT *,
       CASE WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At risk'
            WHEN f_score = 1  AND r_score >= 4 THEN 'New'
            WHEN f_score <= 2 AND r_score <= 2 THEN 'Lapsed one-timers'
            ELSE 'Occasional' END                               AS segment
FROM scored;
