# NYC Yellow Taxi Data Pipeline

An end-to-end data pipeline built using real NYC Yellow Taxi trip data.

## Project Overview

This project demonstrates how raw real-world taxi trip data can be transformed into a validated analytical dataset and business dashboard.

The pipeline covers:

- Data ingestion
- Data profiling
- Data quality validation
- Python transformation
- PostgreSQL staging
- Data warehouse modeling
- Analytical SQL
- Power BI dashboarding

## Architecture

```text
NYC TLC
   ↓
Parquet
   ↓
Python
   ├── Profiling
   ├── Validation
   ├── Cleaning
   └── Anomaly Detection
   ↓
PostgreSQL Staging
   ↓
Star Schema Warehouse
   ↓
Analytics Mart
   ↓
Power BI


## Dashboard Preview

### Executive Overview

![Executive Overview](images/executive_overview.png)

### Zone & Route Analysis

![Zone & Route Analysis](images/zone_route_analysis.png)

### Data Quality

![Data Quality](images/data_quality.png)