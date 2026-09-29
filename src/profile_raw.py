import pandas as pd
from pathlib import Path

# -----------------------------
# 1. Load raw data
# -----------------------------
file_path = Path("data/raw/yellow_tripdata_2026-01.parquet")

df = pd.read_parquet(file_path, engine="pyarrow")

print("=" * 60)
print("RAW DATA PROFILE")
print("=" * 60)

# -----------------------------
# 2. Basic information
# -----------------------------
print("\nBASIC INFORMATION")
print("-" * 60)

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nData types:")
print(df.dtypes)

# -----------------------------
# 3. Missing values
# -----------------------------
print("\nMISSING VALUES")
print("-" * 60)

missing = pd.DataFrame({
    "missing_count": df.isna().sum(),
    "missing_percentage": (df.isna().mean() * 100).round(2)
})

print(missing[missing["missing_count"] > 0])

# -----------------------------
# 4. Duplicate rows
# -----------------------------
print("\nDUPLICATES")
print("-" * 60)

duplicate_count = df.duplicated().sum()

print("Duplicate rows:", duplicate_count)

# -----------------------------
# 5. Date range
# -----------------------------
print("\nDATE RANGE")
print("-" * 60)

print("Pickup start :", df["tpep_pickup_datetime"].min())
print("Pickup end   :", df["tpep_pickup_datetime"].max())

print("Dropoff start:", df["tpep_dropoff_datetime"].min())
print("Dropoff end  :", df["tpep_dropoff_datetime"].max())

# -----------------------------
# 6. Numerical summary
# -----------------------------
print("\nNUMERICAL SUMMARY")
print("-" * 60)

numeric_columns = [
    "passenger_count",
    "trip_distance",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "Airport_fee",
    "cbd_congestion_fee"
]

print(df[numeric_columns].describe().T)

# -----------------------------
# 7. Negative values
# -----------------------------
print("\nNEGATIVE VALUES")
print("-" * 60)

for col in numeric_columns:
    count = (df[col] < 0).sum()

    if count > 0:
        print(f"{col}: {count}")

# -----------------------------
# 8. Zero values
# -----------------------------
print("\nZERO VALUES")
print("-" * 60)

for col in numeric_columns:
    count = (df[col] == 0).sum()
    print(f"{col}: {count}")

# -----------------------------
# 9. Passenger count checks
# -----------------------------
print("\nPASSENGER COUNT CHECK")
print("-" * 60)

print("Passenger count <= 0:",
      (df["passenger_count"] <= 0).sum())

# -----------------------------
# 10. Trip distance checks
# -----------------------------
print("\nTRIP DISTANCE CHECK")
print("-" * 60)

print("Trip distance <= 0:",
      (df["trip_distance"] <= 0).sum())

# -----------------------------
# 11. Duration
# -----------------------------
print("\nTRIP DURATION CHECK")
print("-" * 60)

duration = (
    df["tpep_dropoff_datetime"]
    - df["tpep_pickup_datetime"]
).dt.total_seconds() / 60

print("Negative duration:",
      (duration < 0).sum())

print("Zero duration:",
      (duration == 0).sum())

print("Trips over 24 hours:",
      (duration > 1440).sum())

# -----------------------------
# 12. Categorical values
# -----------------------------
print("\nCATEGORICAL VALUES")
print("-" * 60)

for col in [
    "VendorID",
    "RatecodeID",
    "store_and_fwd_flag",
    "payment_type"
]:
    print(f"\n{col}:")
    print(df[col].value_counts(dropna=False))

# -----------------------------
# Finished
# -----------------------------

print("\n" + "=" * 60)
print("PROFILE COMPLETE")
print("=" * 60)