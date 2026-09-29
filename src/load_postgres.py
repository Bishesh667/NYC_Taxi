import getpass
from io import StringIO
from pathlib import Path

import pandas as pd
import psycopg2
import pyarrow.parquet as pq


# ============================================================
# CONFIGURATION
# ============================================================

PARQUET_FILE = Path(
    "data/processed/yellow_tripdata_2026-01_clean.parquet"
)

HOST = "localhost"
PORT = 5432
DATABASE = "nyc_taxi_dw"
USER = "postgres"

BATCH_SIZE = 100_000


# ============================================================
# GET POSTGRESQL PASSWORD
# ============================================================

password = getpass.getpass(
    "PostgreSQL password: "
)


# ============================================================
# CONNECT TO POSTGRESQL
# ============================================================

print("Connecting to PostgreSQL...")

conn = psycopg2.connect(
    host=HOST,
    port=PORT,
    database=DATABASE,
    user=USER,
    password=password
)

cursor = conn.cursor()

print("Connected successfully.")


# ============================================================
# CLEAR EXISTING STAGING DATA
# ============================================================

print("Clearing staging table...")

cursor.execute(
    "TRUNCATE TABLE staging.yellow_taxi_trips;"
)

conn.commit()

print("Staging table cleared.")


# ============================================================
# COLUMN ORDER
# ============================================================

columns = [
    "vendor_id",
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
    "passenger_count",
    "trip_distance",
    "ratecode_id",
    "store_and_fwd_flag",
    "pulocation_id",
    "dolocation_id",
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
    "cbd_congestion_fee",
    "trip_duration_minutes",
    "pickup_date",
    "pickup_hour",
    "pickup_day_of_week",
    "missing_datetime",
    "negative_duration",
    "duration_over_24_hours",
    "negative_distance",
    "zero_distance",
    "negative_passenger_count",
    "zero_passenger_count",
    "missing_passenger_count",
    "negative_total_amount",
    "zero_duration",
    "missing_location",
    "is_valid_record",
    "fare_per_mile"
]


# ============================================================
# OPEN PARQUET
# ============================================================

print("\nOpening Parquet file...")

parquet = pq.ParquetFile(
    PARQUET_FILE
)

total_rows = parquet.metadata.num_rows

print(
    f"Total rows to load: {total_rows:,}"
)


# ============================================================
# LOAD IN BATCHES
# ============================================================

loaded_rows = 0

try:

    for batch_number, batch in enumerate(
        parquet.iter_batches(
            batch_size=BATCH_SIZE
        ),
        start=1
    ):

        print(
            f"\nProcessing batch {batch_number}..."
        )

        # ----------------------------------------------------
        # Convert batch to Pandas
        # ----------------------------------------------------

        df = batch.to_pandas()


        # ----------------------------------------------------
        # Rename columns
        # ----------------------------------------------------

        rename_map = {
            "vendorid": "vendor_id",
            "ratecodeid": "ratecode_id",
            "pulocationid": "pulocation_id",
            "dolocationid": "dolocation_id"
        }

        df = df.rename(
            columns=rename_map
        )


        # ----------------------------------------------------
        # Convert ID columns to nullable integers
        # ----------------------------------------------------
        # This prevents values like 1.0 being sent to
        # PostgreSQL SMALLINT / INTEGER columns.
        # ----------------------------------------------------

        integer_columns = [
            "vendor_id",
            "ratecode_id",
            "pulocation_id",
            "dolocation_id",
            "payment_type",
            "pickup_hour"
        ]

        for column in integer_columns:

            df[column] = (
                pd.to_numeric(
                    df[column],
                    errors="coerce"
                )
                .astype("Int64")
            )


        # ----------------------------------------------------
        # Convert pickup date
        # ----------------------------------------------------

        df["pickup_date"] = (
            pd.to_datetime(
                df["pickup_date"],
                errors="coerce"
            )
            .dt.strftime("%Y-%m-%d")
        )


        # ----------------------------------------------------
        # Make sure Boolean columns are proper booleans
        # ----------------------------------------------------

        boolean_columns = [
            "missing_datetime",
            "negative_duration",
            "duration_over_24_hours",
            "negative_distance",
            "zero_distance",
            "negative_passenger_count",
            "zero_passenger_count",
            "missing_passenger_count",
            "negative_total_amount",
            "zero_duration",
            "missing_location",
            "is_valid_record"
        ]

        for column in boolean_columns:

            df[column] = df[column].astype("boolean")


        # ----------------------------------------------------
        # Select columns in PostgreSQL order
        # ----------------------------------------------------

        df = df[columns]


        # ----------------------------------------------------
        # Convert DataFrame to CSV in memory
        # ----------------------------------------------------

        buffer = StringIO()

        df.to_csv(
            buffer,
            index=False,
            header=False,
            na_rep="\\N"
        )

        buffer.seek(0)


        # ----------------------------------------------------
        # COPY into PostgreSQL
        # ----------------------------------------------------

        cursor.copy_expert(
            """
            COPY staging.yellow_taxi_trips
            FROM STDIN
            WITH (
                FORMAT CSV,
                NULL '\\N'
            )
            """,
            buffer
        )


        # ----------------------------------------------------
        # Commit batch
        # ----------------------------------------------------

        conn.commit()


        # ----------------------------------------------------
        # Progress
        # ----------------------------------------------------

        loaded_rows += len(df)

        percentage = (
            loaded_rows
            / total_rows
            * 100
        )

        print(
            f"Loaded: {loaded_rows:,} / "
            f"{total_rows:,} "
            f"({percentage:.2f}%)"
        )


    # ========================================================
    # SUCCESS
    # ========================================================

    print("\n" + "=" * 60)
    print("POSTGRESQL LOAD COMPLETE")
    print("=" * 60)

    print(
        f"Rows loaded: {loaded_rows:,}"
    )


except Exception as e:

    # ========================================================
    # ERROR
    # ========================================================

    conn.rollback()

    print("\n" + "=" * 60)
    print("ERROR DURING POSTGRESQL LOAD")
    print("=" * 60)

    print(e)

    raise


finally:

    cursor.close()
    conn.close()

    print("\nPostgreSQL connection closed.")