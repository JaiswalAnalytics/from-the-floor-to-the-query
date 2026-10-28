import os, duckdb
os.chdir(os.path.dirname(os.path.abspath(__file__)))
con = duckdb.connect()
con.execute("CREATE TABLE orders AS SELECT order_id, customer_id, customer_type, CAST(order_date AS DATE) order_date, order_value, cogs, delivered, delivery_cost, credit_days, bad_debt FROM read_csv_auto('data/orders.csv')")
con.execute("CREATE TABLE fixed_costs AS SELECT * FROM read_csv_auto('data/fixed_costs.csv')")
for name in ["contribution_by_type", "store_pl"]:
    df = con.execute(open(f"sql/{name}.sql").read()).df()
    df.to_csv(f"results/sql_{name}.csv", index=False)
    print(df.to_string(index=False)); print()
