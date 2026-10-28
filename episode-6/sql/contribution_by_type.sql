-- Episode 6: gross margin vs contribution margin by customer type (DuckDB)
-- Contribution = gross profit - delivery - credit cost (18% a year on the days credit is out) - bad debt
SELECT customer_type,
       COUNT(*)                                                        AS orders,
       SUM(order_value)                                                AS revenue,
       ROUND(SUM(order_value - cogs))                                  AS gross_profit,
       ROUND(100.0 * SUM(order_value - cogs) / SUM(order_value), 1)    AS gross_margin_pct,
       ROUND(SUM(order_value - cogs - delivery_cost
                 - order_value * 0.18 * credit_days / 365
                 - order_value * bad_debt))                            AS contribution,
       ROUND(100.0 * SUM(order_value - cogs - delivery_cost
                 - order_value * 0.18 * credit_days / 365
                 - order_value * bad_debt) / SUM(order_value), 1)      AS contribution_margin_pct,
       ROUND(SUM(order_value - cogs - delivery_cost
                 - order_value * 0.18 * credit_days / 365
                 - order_value * bad_debt) / COUNT(*))                 AS contribution_per_order
FROM orders
GROUP BY customer_type
ORDER BY revenue DESC;
