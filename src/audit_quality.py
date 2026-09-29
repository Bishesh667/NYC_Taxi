import pandas as pd
from pathlib import Path


RAW_FILE = Path("data/raw/yellow_tripdata_2026-01.parquet")

df = pd.read_parquet(
    RAW_FILE,
    engine="pyarrow"
)

print("=" * 70)
print("DATA QUALITY AUDIT")
print("=" * 70)


# ------------------------------------------------------------
# 1. PAYMENT TYPES
# ------------------------------------------------------------

print("\nPAYMENT TYPES")
print("-" * 70)

print(
    df["payment_type"]
    .value_counts(dropna=False)
    .sort_index()
)


# ------------------------------------------------------------
# 2. NEGATIVE TOTAL AMOUNTS
# ------------------------------------------------------------

negative_total = df[df["total_amount"] < 0]

print("\nNEGATIVE TOTAL AMOUNT")
print("-" * 70)

print("Count:", len(negative_total))

print("\nPayment types:")
print(
    negative_total["payment_type"]
    .value_counts(dropna=False)
    .sort_index()
)

print("\nSample:")
print(
    negative_total[
        [
            "payment_type",
            "fare_amount",
            "tip_amount",
            "total_amount",
            "trip_distance"
        ]
    ].head(20)
)


# ------------------------------------------------------------
# 3. PASSENGER COUNT
# ------------------------------------------------------------

print("\nPASSENGER COUNT")
print("-" * 70)

print(
    df["passenger_count"]
    .value_counts(dropna=False)
    .sort_index()
)

print(
    "\nPassenger count < 0:",
    (df["passenger_count"] < 0).sum()
)

print(
    "Passenger count = 0:",
    (df["passenger_count"] == 0).sum()
)


# ------------------------------------------------------------
# 4. TRIP DISTANCE
# ------------------------------------------------------------

print("\nTRIP DISTANCE")
print("-" * 70)

print(
    "Distance < 0:",
    (df["trip_distance"] < 0).sum()
)

print(
    "Distance = 0:",
    (df["trip_distance"] == 0).sum()
)

print(
    "\nDistance summary:"
)

print(
    df["trip_distance"].describe()
)


# ------------------------------------------------------------
# 5. TRIP DURATION
# ------------------------------------------------------------

df["pickup"] = pd.to_datetime(
    df["tpep_pickup_datetime"],
    errors="coerce"
)

df["dropoff"] = pd.to_datetime(
    df["tpep_dropoff_datetime"],
    errors="coerce"
)

df["duration_minutes"] = (
    df["dropoff"] - df["pickup"]
).dt.total_seconds() / 60


print("\nTRIP DURATION")
print("-" * 70)

print(
    "Negative duration:",
    (df["duration_minutes"] < 0).sum()
)

print(
    "Zero duration:",
    (df["duration_minutes"] == 0).sum()
)

print(
    "Over 24 hours:",
    (df["duration_minutes"] > 1440).sum()
)


# ------------------------------------------------------------
# 6. COMBINED SUSPICIOUS RECORDS
# ------------------------------------------------------------

print("\nSUSPICIOUS RECORD OVERLAPS")
print("-" * 70)

negative_amount = df["total_amount"] < 0
zero_passenger = df["passenger_count"] == 0
negative_passenger = df["passenger_count"] < 0
zero_distance = df["trip_distance"] == 0
negative_distance = df["trip_distance"] < 0
negative_duration = df["duration_minutes"] < 0
long_duration = df["duration_minutes"] > 1440


checks = pd.DataFrame({
    "negative_amount": negative_amount,
    "zero_passenger": zero_passenger,
    "negative_passenger": negative_passenger,
    "zero_distance": zero_distance,
    "negative_distance": negative_distance,
    "negative_duration": negative_duration,
    "over_24_hours": long_duration
})

print("\nNumber of records triggering each rule:")

print(
    checks.sum()
)


# ------------------------------------------------------------
# 7. NEGATIVE AMOUNT + PAYMENT TYPE
# ------------------------------------------------------------

print("\nNEGATIVE AMOUNT BY PAYMENT TYPE")
print("-" * 70)

negative_payment = (
    df.loc[
        negative_amount,
        ["payment_type", "total_amount"]
    ]
    .groupby("payment_type")
    .agg(
        records=("total_amount", "size"),
        total_negative_amount=("total_amount", "sum"),
        minimum_amount=("total_amount", "min")
    )
    .sort_index()
)

print(negative_payment)


# ------------------------------------------------------------
# COMPLETE
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("AUDIT COMPLETE")
print("=" * 70)