-- Episode 6: store profit and loss for the year (DuckDB)
WITH o AS (
    SELECT SUM(order_value) AS revenue,
           SUM(order_value - cogs) AS gross_profit,
           SUM(delivery_cost) AS delivery,
           SUM(order_value * 0.18 * credit_days / 365) AS credit_cost,
           SUM(order_value * bad_debt) AS bad_debt
    FROM orders
),
f AS (SELECT SUM(rent + salaries + electricity + other) AS fixed_costs FROM fixed_costs)
SELECT revenue, gross_profit, delivery, ROUND(credit_cost) AS credit_cost, bad_debt,
       ROUND(gross_profit - delivery - credit_cost - bad_debt) AS contribution,
       fixed_costs,
       ROUND(gross_profit - delivery - credit_cost - bad_debt - fixed_costs) AS operating_profit,
       ROUND(fixed_costs / ((gross_profit - delivery - credit_cost - bad_debt) / revenue)) AS breakeven_revenue_year
FROM o, f;
