"""Runs sql/scorecard.sql in DuckDB and saves results/scorecard.csv. Run from the episode-9 folder."""
import duckdb, pandas as pd
pd.set_option("display.width", 250, "display.max_columns", 30)
df = duckdb.sql(open("sql/scorecard.sql").read()).df()
df.to_csv("results/scorecard.csv", index=False)
print(df.to_string(index=False))
