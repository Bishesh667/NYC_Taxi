import pandas as pd
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

RAW_FILE = Path(
    "data/raw/yellow_tripdata_2026-01.parquet"
)

PROCESSED_DIR = Path(
    "data/processed"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CLEAN_FILE = (
    PROCESSED_DIR /
    "yellow_tripdata_2026-01_clean.parquet"
)

VALID_FILE = (
    PROCESSED_DIR /
    "yellow_tripdata_2026-01_valid.parquet"
)

QUALITY_FILE = (
    PROCESSED_DIR /
    "data_quality_report.csv"
)


# ============================================================
# 1. LOAD RAW DATA
# ============================================================

print("Loading raw data...")

df = pd.read_parquet(
    RAW_FILE,
    engine="pyarrow"
)

raw_rows = len(df)

print(f"Raw rows: {raw_rows:,}")


# ============================================================
# 2. STANDARDIZE COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
)


# ============================================================
# 3. DATETIME
# ============================================================

datetime_columns = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

for column in datetime_columns:

    df[column] = pd.to_datetime(
        df[column],
        errors="coerce"
    )


# ============================================================
# 4. NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "vendorid",
    "passenger_count",
    "trip_distance",
    "ratecodeid",
    "pulocationid",
    "dolocationid",
    "payment_type",
    "fare_amount",
    "extra",
    "mta_tax",
    "tip_amount",
    "tolls_amount",
    "improvement_surcharge",
    "total_amount",
    "congestion_surcharge",
    "airport_fee",
    "cbd_congestion_fee"
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# ============================================================
# 5. TRIP DURATION
# ============================================================

df["trip_duration_minutes"] = (
    df["tpep_dropoff_datetime"]
    - df["tpep_pickup_datetime"]
).dt.total_seconds() / 60


# ============================================================
# 6. DATE / TIME FEATURES
# ============================================================

df["pickup_date"] = (
    df["tpep_pickup_datetime"].dt.date
)

df["pickup_hour"] = (
    df["tpep_pickup_datetime"].dt.hour
)

df["pickup_day_of_week"] = (
    df["tpep_pickup_datetime"].dt.day_name()
)


# ============================================================
# 7. ANOMALY FLAGS
# ============================================================

df["missing_datetime"] = (
    df["tpep_pickup_datetime"].isna()
    |
    df["tpep_dropoff_datetime"].isna()
)

df["negative_duration"] = (
    df["trip_duration_minutes"] < 0
)

df["duration_over_24_hours"] = (
    df["trip_duration_minutes"] > 1440
)

df["negative_distance"] = (
    df["trip_distance"] < 0
)

df["zero_distance"] = (
    df["trip_distance"] == 0
)

df["negative_passenger_count"] = (
    df["passenger_count"] < 0
)

df["zero_passenger_count"] = (
    df["passenger_count"] == 0
)

df["missing_passenger_count"] = (
    df["passenger_count"].isna()
)

df["negative_total_amount"] = (
    df["total_amount"] < 0
)

df["zero_duration"] = (
    df["trip_duration_minutes"] == 0
)

df["missing_location"] = (
    df["pulocationid"].isna()
    |
    df["dolocationid"].isna()
)


# ============================================================
# 8. VALIDATION
# ============================================================

df["is_valid_record"] = (
    ~df["missing_datetime"]
    &
    ~df["negative_duration"]
    &
    ~df["duration_over_24_hours"]
    &
    ~df["negative_distance"]
    &
    ~df["negative_passenger_count"]
    &
    ~df["missing_location"]
)


# ============================================================
# 9. BUSINESS METRICS
# ============================================================

df["fare_per_mile"] = (
    df["total_amount"]
    /
    df["trip_distance"].replace(0, pd.NA)
)


# ============================================================
# 10. QUALITY REPORT
# ============================================================

quality_checks = {

    "raw_rows":
        len(df),

    "missing_datetime":
        int(df["missing_datetime"].sum()),

    "negative_duration":
        int(df["negative_duration"].sum()),

    "duration_over_24_hours":
        int(df["duration_over_24_hours"].sum()),

    "negative_distance":
        int(df["negative_distance"].sum()),

    "zero_distance":
        int(df["zero_distance"].sum()),

    "negative_passenger_count":
        int(df["negative_passenger_count"].sum()),

    "zero_passenger_count":
        int(df["zero_passenger_count"].sum()),

    "missing_passenger_count":
        int(df["missing_passenger_count"].sum()),

    "negative_total_amount":
        int(df["negative_total_amount"].sum()),

    "zero_duration":
        int(df["zero_duration"].sum()),

    "missing_location":
        int(df["missing_location"].sum()),

    "valid_records":
        int(df["is_valid_record"].sum()),

    "invalid_records":
        int((~df["is_valid_record"]).sum())
}


quality_report = pd.DataFrame(
    list(quality_checks.items()),
    columns=[
        "metric",
        "count"
    ]
)

quality_report["percentage"] = (
    quality_report["count"]
    / raw_rows
    * 100
).round(2)


# ============================================================
# 11. SAVE ALL CLEANED RECORDS
# ============================================================

print("\nSaving cleaned data...")

df.to_parquet(
    CLEAN_FILE,
    engine="pyarrow",
    index=False
)


# ============================================================
# 12. SAVE VALID RECORDS
# ============================================================

valid_df = df[
    df["is_valid_record"]
].copy()

print("Saving valid records...")

valid_df.to_parquet(
    VALID_FILE,
    engine="pyarrow",
    index=False
)


# ============================================================
# 13. SAVE QUALITY REPORT
# ============================================================

quality_report.to_csv(
    QUALITY_FILE,
    index=False
)


# ============================================================
# 14. OUTPUT
# ============================================================

print("\n" + "=" * 60)
print("PIPELINE CLEANING COMPLETE")
print("=" * 60)

print(
    f"Raw records:       {len(df):,}"
)

print(
    f"Valid records:     {len(valid_df):,}"
)

print(
    f"Invalid records:   {len(df) - len(valid_df):,}"
)

print("\nQuality report:")

print(
    quality_report.to_string(
        index=False
    )
)

print("\nCreated:")

print(CLEAN_FILE)
print(VALID_FILE)
print(QUALITY_FILE)