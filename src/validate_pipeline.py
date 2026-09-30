import sys
import getpass

import psycopg2


# ============================================================
# CONFIGURATION
# ============================================================

HOST = "localhost"
PORT = 5432
DATABASE = "nyc_taxi_dw"
USER = "postgres"

EXPECTED_STAGING_ROWS = 3_724_889
EXPECTED_WAREHOUSE_ROWS = 3_724_853
EXPECTED_ZONE_ROWS = 265


# ============================================================
# CONNECT
# ============================================================

password = getpass.getpass("PostgreSQL password: ")

conn = psycopg2.connect(
    host=HOST,
    port=PORT,
    database=DATABASE,
    user=USER,
    password=password
)

cursor = conn.cursor()

print("\nConnected to PostgreSQL.")
print("=" * 60)
print("PIPELINE VALIDATION")
print("=" * 60)


failures = []


# ============================================================
# 1. STAGING ROW COUNT
# ============================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM staging.yellow_taxi_trips;
""")

staging_rows = cursor.fetchone()[0]

print(
    f"\nStaging rows: {staging_rows:,}"
)

if staging_rows != EXPECTED_STAGING_ROWS:
    failures.append(
        f"Expected {EXPECTED_STAGING_ROWS:,} staging rows "
        f"but found {staging_rows:,}"
    )
else:
    print("PASS: staging row count")


# ============================================================
# 2. WAREHOUSE ROW COUNT
# ============================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM warehouse.fact_trips;
""")

warehouse_rows = cursor.fetchone()[0]

print(
    f"Warehouse rows: {warehouse_rows:,}"
)

if warehouse_rows != EXPECTED_WAREHOUSE_ROWS:
    failures.append(
        f"Expected {EXPECTED_WAREHOUSE_ROWS:,} warehouse rows "
        f"but found {warehouse_rows:,}"
    )
else:
    print("PASS: warehouse row count")


# ============================================================
# 3. ZONE LOOKUP COUNT
# ============================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM staging.taxi_zone_lookup;
""")

zone_rows = cursor.fetchone()[0]

print(
    f"Zone lookup rows: {zone_rows:,}"
)

if zone_rows != EXPECTED_ZONE_ROWS:
    failures.append(
        f"Expected {EXPECTED_ZONE_ROWS:,} zone rows "
        f"but found {zone_rows:,}"
    )
else:
    print("PASS: zone lookup count")


# ============================================================
# 4. NEGATIVE DISTANCE
# ============================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM staging.yellow_taxi_trips
    WHERE negative_distance = TRUE;
""")

negative_distance = cursor.fetchone()[0]

print(
    f"Negative distance records: {negative_distance:,}"
)

if negative_distance != 0:
    failures.append(
        f"Found {negative_distance:,} negative-distance records"
    )
else:
    print("PASS: no negative distances")


# ============================================================
# 5. NEGATIVE PASSENGER COUNT
# ============================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM staging.yellow_taxi_trips
    WHERE negative_passenger_count = TRUE;
""")

negative_passengers = cursor.fetchone()[0]

print(
    f"Negative passenger records: {negative_passengers:,}"
)

if negative_passengers != 0:
    failures.append(
        f"Found {negative_passengers:,} negative passenger records"
    )
else:
    print("PASS: no negative passenger counts")


# ============================================================
# 6. INVALID RECORDS EXCLUDED FROM FACT
# ============================================================

cursor.execute("""
    SELECT COUNT(*)
    FROM staging.yellow_taxi_trips
    WHERE is_valid_record = FALSE;
""")

invalid_records = cursor.fetchone()[0]

print(
    f"Invalid staging records: {invalid_records:,}"
)

expected_invalid = (
    EXPECTED_STAGING_ROWS
    - EXPECTED_WAREHOUSE_ROWS
)

if invalid_records != expected_invalid:
    failures.append(
        f"Expected {expected_invalid:,} invalid records "
        f"but found {invalid_records:,}"
    )
else:
    print("PASS: invalid-record count")


# ============================================================
# 7. ANALYTICS TABLES
# ============================================================

analytics_tables = [
    "daily_trip_summary",
    "hourly_trip_summary",
    "zone_performance",
    "payment_performance",
    "route_performance"
]

for table in analytics_tables:

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM analytics.{table};
        """
    )

    count = cursor.fetchone()[0]

    print(
        f"{table}: {count:,} rows"
    )

    if count == 0:
        failures.append(
            f"Analytics table {table} is empty"
        )
    else:
        print(
            f"PASS: {table}"
        )


# ============================================================
# RESULT
# ============================================================

cursor.close()
conn.close()


print("\n" + "=" * 60)

if failures:

    print("PIPELINE VALIDATION FAILED")
    print("=" * 60)

    for failure in failures:
        print(f"- {failure}")

    sys.exit(1)

else:

    print("PIPELINE VALIDATION PASSED")
    print("=" * 60)

    print(
        "\nAll expected data-quality checks passed."
    )

    sys.exit(0)