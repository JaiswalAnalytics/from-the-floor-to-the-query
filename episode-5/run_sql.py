import os, duckdb
os.chdir(os.path.dirname(os.path.abspath(__file__)))
con = duckdb.connect()
con.execute("CREATE TABLE orders AS SELECT order_id, customer_id, CAST(order_date AS DATE) order_date, order_value FROM read_csv_auto('data/orders.csv')")
con.execute("CREATE TABLE customers AS SELECT * FROM read_csv_auto('data/customers.csv')")
df = con.execute(open('sql/cohort_retention.sql').read()).df()
df.to_csv('results/cohort_retention.csv', index=False)
print(df.pivot(index='cohort_month', columns='month_n', values='retention_pct').round(1).to_string())
