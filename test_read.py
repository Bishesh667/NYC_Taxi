import pandas as pd

file_path = "data/raw/yellow_tripdata_2026-01.parquet"

df = pd.read_parquet(file_path, engine="pyarrow")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())

print("\nFirst 5 rows:")
print(df.head())