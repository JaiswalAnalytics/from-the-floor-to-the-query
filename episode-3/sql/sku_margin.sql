-- Episode 3: gross margin by SKU, revenue rank vs profit rank
WITH line AS (
    SELECT s.sku_id, k.sku_name, k.category,
           s.qty * s.unit_price  AS revenue,
           s.qty * k.cost_price  AS cogs
    FROM sales_lines s
    JOIN skus k USING (sku_id)
),
sku_margin AS (
    SELECT sku_id, sku_name, category,
           SUM(revenue)              AS revenue,
           SUM(cogs)                 AS cogs,
           SUM(revenue) - SUM(cogs)  AS gross_profit
    FROM line
    GROUP BY sku_id, sku_name, category
)
SELECT sku_name, category,
       ROUND(revenue)                                       AS revenue,
       ROUND(gross_profit)                                  AS gross_profit,
       ROUND(100.0 * gross_profit / revenue, 1)             AS margin_pct,
       RANK() OVER (ORDER BY revenue DESC)                  AS revenue_rank,
       RANK() OVER (ORDER BY gross_profit DESC)             AS profit_rank,
       ROUND(100.0 * SUM(gross_profit) OVER (ORDER BY gross_profit DESC)
             / SUM(gross_profit) OVER (), 1)                AS cum_profit_pct
FROM sku_margin
ORDER BY gross_profit DESC;
