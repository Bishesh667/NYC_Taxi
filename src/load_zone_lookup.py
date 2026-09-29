import pandas as pd
import psycopg2
from io import StringIO
from pathlib import Path
import getpass


# ============================================================
# CONFIG
# ============================================================

CSV_FILE = Path(
    "data/raw/taxi_zone_lookup.csv"
)

HOST = "localhost"
PORT = 5432
DATABASE = "nyc_taxi_dw"
USER = "postgres"


# ============================================================
# PASSWORD
# ============================================================

password = getpass.getpass(
    "PostgreSQL password: "
)


# ============================================================
# CONNECT
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
# LOAD CSV
# ============================================================

print("\nReading taxi zone lookup...")

df = pd.read_csv(CSV_FILE)

print(f"Rows in CSV: {len(df):,}")

print("\nColumns found:")
print(df.columns.tolist())


# ============================================================
# STANDARDIZE COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)


# ============================================================
# RENAME LOCATION ID
# ============================================================

df = df.rename(
    columns={
        "locationid": "location_id"
    }
)


# ============================================================
# KEEP REQUIRED COLUMNS
# ============================================================

df = df[
    [
        "location_id",
        "borough",
        "zone",
        "service_zone"
    ]
]


# ============================================================
# CLEAR EXISTING TABLE
# ============================================================

print("\nClearing existing zone lookup...")

cursor.execute(
    "TRUNCATE TABLE staging.taxi_zone_lookup;"
)

conn.commit()


# ============================================================
# CONVERT TO CSV IN MEMORY
# ============================================================

buffer = StringIO()

df.to_csv(
    buffer,
    index=False,
    header=False,
    na_rep="\\N"
)

buffer.seek(0)


# ============================================================
# LOAD INTO POSTGRESQL
# ============================================================

cursor.copy_expert(
    """
    COPY staging.taxi_zone_lookup
    FROM STDIN
    WITH (
        FORMAT CSV,
        NULL '\\N'
    )
    """,
    buffer
)

conn.commit()


# ============================================================
# VERIFY
# ============================================================

cursor.execute(
    "SELECT COUNT(*) FROM staging.taxi_zone_lookup;"
)

count = cursor.fetchone()[0]


print("\n" + "=" * 60)
print("ZONE LOOKUP LOAD COMPLETE")
print("=" * 60)

print(
    f"Rows loaded: {count:,}"
)


# ============================================================
# CLOSE
# ============================================================

cursor.close()
conn.close()

print("\nPostgreSQL connection closed.")