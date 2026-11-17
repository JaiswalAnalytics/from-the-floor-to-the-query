-- Supplier scorecard. Run with DuckDB from the episode-9 folder (see run_sql.py).
-- Weights are an ASSUMPTION: on time 35, fill 25, quality 25, price 15.
-- "Price first" weights are the sensitivity check: on time 15, fill 10, quality 25, price 50.
WITH po AS (
  SELECT * FROM 'data/purchase_orders.csv'
),
m AS (                                   -- one row per supplier: the raw metrics
  SELECT supplier,
         count(*)                                                        AS pos,
         100.0 * avg((received_date <= promised_date)::INT)              AS on_time_pct,
         avg(CASE WHEN received_date > promised_date
                  THEN date_diff('day', promised_date, received_date) END) AS avg_days_late,
         100.0 * sum(qty_received) / sum(qty_ordered)                    AS fill_pct,
         100.0 * sum(qty_rejected) / sum(qty_received)                   AS reject_pct,
         sum(invoiced_rate * qty_received) / sum(market_rate * qty_received) AS price_idx,
         sum(invoiced_rate * qty_received)
           / sum(market_rate * (qty_received - qty_rejected))            AS usable_price_idx,
         sum(invoiced_rate * qty_received)                               AS paid_value
  FROM po GROUP BY supplier
),
s AS (                                   -- turn each metric into 0 to 100 points
  SELECT *,
         on_time_pct                                              AS on_time_pts,
         fill_pct                                                 AS fill_pts,
         greatest(0, 100 - 10 * reject_pct)                       AS quality_pts,
         least(100, greatest(0, 100 - 1000 * (price_idx - 0.95))) AS price_pts
  FROM m
),
sc AS (
  SELECT *,
         0.35*on_time_pts + 0.25*fill_pts + 0.25*quality_pts + 0.15*price_pts AS score,
         0.15*on_time_pts + 0.10*fill_pts + 0.25*quality_pts + 0.50*price_pts AS score_price_first
  FROM s
)
SELECT supplier, pos,
       round(on_time_pct, 1)  AS on_time_pct,
       round(avg_days_late, 1) AS avg_days_late,
       round(fill_pct, 1)     AS fill_pct,
       round(reject_pct, 1)   AS reject_pct,
       round(price_idx, 3)    AS price_idx,
       round(usable_price_idx, 3) AS usable_price_idx,
       round(paid_value, 0)   AS paid_value,
       round(score, 1)        AS score,
       rank() OVER (ORDER BY price_idx)              AS price_rank,
       rank() OVER (ORDER BY score DESC)             AS score_rank,
       round(score_price_first, 1)                   AS score_price_first,
       rank() OVER (ORDER BY score_price_first DESC) AS price_first_rank
FROM sc
ORDER BY score DESC;
