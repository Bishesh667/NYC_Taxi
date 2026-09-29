-- ============================================================
-- NYC TAXI ANALYTICS / DATA MART LAYER
-- ============================================================

CREATE SCHEMA IF NOT EXISTS analytics;


-- ============================================================
-- DROP EXISTING MARTS
-- ============================================================

DROP TABLE IF EXISTS analytics.daily_trip_summary;
DROP TABLE IF EXISTS analytics.hourly_trip_summary;
DROP TABLE IF EXISTS analytics.zone_performance;
DROP TABLE IF EXISTS analytics.payment_performance;
DROP TABLE IF EXISTS analytics.route_performance;


-- ============================================================
-- 1. DAILY TRIP SUMMARY
-- ============================================================

CREATE TABLE analytics.daily_trip_summary AS

SELECT
    d.full_date,

    COUNT(*) AS total_trips,

    SUM(
        CASE
            WHEN f.total_amount > 0
            THEN f.total_amount
            ELSE 0
        END
    ) AS positive_trip_revenue,

    SUM(
        CASE
            WHEN f.total_amount < 0
            THEN f.total_amount
            ELSE 0
        END
    ) AS negative_adjustments,

    SUM(f.total_amount) AS net_revenue,

    SUM(f.tip_amount) AS total_tips,

    AVG(f.total_amount) AS avg_trip_value,

    AVG(f.trip_distance) AS avg_trip_distance,

    AVG(f.trip_duration_minutes) AS avg_trip_duration,

    AVG(f.passenger_count)
        FILTER (
            WHERE f.passenger_count IS NOT NULL
        ) AS avg_passengers,

    COUNT(*)
        FILTER (
            WHERE f.negative_total_amount
        ) AS financial_anomaly_trips,

    COUNT(*)
        FILTER (
            WHERE f.zero_distance
        ) AS zero_distance_trips,

    COUNT(*)
        FILTER (
            WHERE f.zero_duration
        ) AS zero_duration_trips

FROM warehouse.fact_trips f

JOIN warehouse.dim_date d
    ON f.pickup_date_key = d.date_key

GROUP BY
    d.full_date

ORDER BY
    d.full_date;


-- ============================================================
-- 2. HOURLY TRIP SUMMARY
-- ============================================================

CREATE TABLE analytics.hourly_trip_summary AS

SELECT

    EXTRACT(
        HOUR FROM f.pickup_datetime
    )::INTEGER AS pickup_hour,

    COUNT(*) AS total_trips,

    SUM(
        CASE
            WHEN f.total_amount > 0
            THEN f.total_amount
            ELSE 0
        END
    ) AS positive_trip_revenue,

    SUM(f.total_amount) AS net_revenue,

    AVG(f.total_amount) AS avg_trip_value,

    AVG(f.trip_distance) AS avg_trip_distance,

    AVG(f.trip_duration_minutes) AS avg_trip_duration,

    SUM(f.tip_amount) AS total_tips

FROM warehouse.fact_trips f

GROUP BY
    EXTRACT(HOUR FROM f.pickup_datetime)

ORDER BY
    pickup_hour;


-- ============================================================
-- 3. ZONE PERFORMANCE
-- ============================================================

CREATE TABLE analytics.zone_performance AS

SELECT

    z.location_id,

    z.borough,

    z.zone,

    z.service_zone,

    COUNT(*) AS total_trips,

    SUM(
        CASE
            WHEN f.total_amount > 0
            THEN f.total_amount
            ELSE 0
        END
    ) AS positive_trip_revenue,

    SUM(f.total_amount) AS net_revenue,

    SUM(f.tip_amount) AS total_tips,

    AVG(f.total_amount) AS avg_trip_value,

    AVG(f.trip_distance) AS avg_trip_distance,

    AVG(f.trip_duration_minutes) AS avg_trip_duration,

    AVG(f.passenger_count)
        FILTER (
            WHERE f.passenger_count IS NOT NULL
        ) AS avg_passengers,

    COUNT(*)
        FILTER (
            WHERE f.negative_total_amount
        ) AS financial_anomaly_trips,

    COUNT(*)
        FILTER (
            WHERE f.zero_distance
        ) AS zero_distance_trips

FROM warehouse.fact_trips f

JOIN warehouse.dim_zone z
    ON f.pickup_zone_key = z.zone_key

GROUP BY

    z.location_id,
    z.borough,
    z.zone,
    z.service_zone

ORDER BY
    net_revenue DESC;


-- ============================================================
-- 4. PAYMENT PERFORMANCE
-- ============================================================

CREATE TABLE analytics.payment_performance AS

SELECT

    p.payment_type_code,

    p.payment_type_name,

    COUNT(*) AS total_trips,

    SUM(
        CASE
            WHEN f.total_amount > 0
            THEN f.total_amount
            ELSE 0
        END
    ) AS positive_trip_revenue,

    SUM(f.total_amount) AS net_revenue,

    SUM(f.tip_amount) AS total_tips,

    AVG(f.total_amount) AS avg_trip_value,

    AVG(
        CASE
            WHEN f.total_amount > 0
            THEN f.tip_amount
        END
    ) AS avg_tip_on_positive_fare,

    COUNT(*)
        FILTER (
            WHERE f.negative_total_amount
        ) AS negative_amount_trips

FROM warehouse.fact_trips f

JOIN warehouse.dim_payment_type p
    ON f.payment_type_key = p.payment_type_key

GROUP BY

    p.payment_type_code,
    p.payment_type_name

ORDER BY
    total_trips DESC;


-- ============================================================
-- 5. ROUTE PERFORMANCE
-- ============================================================

CREATE TABLE analytics.route_performance AS

SELECT

    pickup.location_id AS pickup_location_id,
    pickup.borough AS pickup_borough,
    pickup.zone AS pickup_zone,

    dropoff.location_id AS dropoff_location_id,
    dropoff.borough AS dropoff_borough,
    dropoff.zone AS dropoff_zone,

    COUNT(*) AS total_trips,

    SUM(
        CASE
            WHEN f.total_amount > 0
            THEN f.total_amount
            ELSE 0
        END
    ) AS positive_trip_revenue,

    SUM(f.total_amount) AS net_revenue,

    AVG(f.total_amount) AS avg_trip_value,

    AVG(f.trip_distance) AS avg_trip_distance,

    AVG(f.trip_duration_minutes) AS avg_trip_duration,

    AVG(f.tip_amount) AS avg_tip

FROM warehouse.fact_trips f

JOIN warehouse.dim_zone pickup
    ON f.pickup_zone_key = pickup.zone_key

JOIN warehouse.dim_zone dropoff
    ON f.dropoff_zone_key = dropoff.zone_key

GROUP BY

    pickup.location_id,
    pickup.borough,
    pickup.zone,

    dropoff.location_id,
    dropoff.borough,
    dropoff.zone

HAVING COUNT(*) >= 10

ORDER BY
    total_trips DESC;