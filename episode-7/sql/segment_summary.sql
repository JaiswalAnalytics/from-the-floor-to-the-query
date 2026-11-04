-- Episode 7: size and money of each segment (DuckDB). Run after creating the view rfm_segments.
SELECT segment,
       COUNT(*)                                                    AS customers,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1)          AS customer_share_pct,
       SUM(monetary)                                               AS revenue,
       ROUND(100.0 * SUM(monetary) / SUM(SUM(monetary)) OVER (), 1) AS revenue_share_pct,
       ROUND(AVG(frequency), 1)                                    AS avg_orders,
       ROUND(AVG(monetary))                                        AS avg_spend,
       ROUND(AVG(recency_days))                                    AS avg_recency_days
FROM rfm_segments
GROUP BY segment
ORDER BY revenue DESC;
