
-- ============================================================
-- Walmart Enterprise Demand Forecasting
-- Build Modeling Dataset
-- ============================================================

-- ============================================================
-- 1. Create reusable modeling view
-- Sales + Calendar + Products + Stores + Prices + Weather
-- + Economic Indicators
-- ============================================================

CREATE OR REPLACE VIEW vw_modeling_dataset AS

SELECT
    -- Sales
    s.date,
    s.item_id,
    s.store_id,
    s.units_sold,

    -- Product information
    p.dept_id,
    p.cat_id,

    -- Store information
    st.state_id,

    -- Calendar information
    c.wday,
    c.month,
    c.year,
    c.wm_yr_wk,
    c.event_name_1,
    c.event_type_1,
    c.event_name_2,
    c.event_type_2,

    -- Event indicator
    CASE
        WHEN c.event_name_1 IS NOT NULL
          OR c.event_name_2 IS NOT NULL
        THEN TRUE
        ELSE FALSE
    END AS is_event_day,

    -- SNAP indicators
    c.snap_ca,
    c.snap_tx,
    c.snap_wi,

    -- Price
    pr.sell_price,

    -- Weather
    w.temperature_max,
    w.temperature_min,
    w.precipitation,
    w.snowfall,
    w.wind_speed_max,

    -- Economic indicators
    econ.cpi,
    econ.unemployment_rate,
    econ.federal_funds_rate

FROM fact_sales AS s

-- ============================================================
-- 2. Join Calendar
-- ============================================================

JOIN dim_calendar AS c
    ON s.date = c.date

-- ============================================================
-- 3. Join Products
-- ============================================================

JOIN dim_product AS p
    ON s.item_id = p.item_id

-- ============================================================
-- 4. Join Stores
-- ============================================================

JOIN dim_store AS st
    ON s.store_id = st.store_id

-- ============================================================
-- 5. Join Prices
-- ============================================================

LEFT JOIN fact_prices AS pr
    ON s.store_id = pr.store_id
    AND s.item_id = pr.item_id
    AND c.wm_yr_wk = pr.wm_yr_wk

-- ============================================================
-- 6. Join Weather
-- ============================================================

LEFT JOIN fact_weather AS w
    ON s.date = w.date
    AND st.state_id = w.state_id

-- ============================================================
-- 7. Join Economic Indicators
-- Use observations from two months earlier as a
-- conservative timing lag.
-- Historical release dates/revisions still need verification.
-- ============================================================

LEFT JOIN LATERAL (
    SELECT
        MAX(e.value) FILTER (
            WHERE e.series_id = 'CPIAUCSL'
        ) AS cpi,

        MAX(e.value) FILTER (
            WHERE e.series_id = 'UNRATE'
        ) AS unemployment_rate,

        MAX(e.value) FILTER (
            WHERE e.series_id = 'FEDFUNDS'
        ) AS federal_funds_rate

    FROM fact_economic_indicator AS e

    WHERE e.observation_date = (
        DATE_TRUNC('month', s.date)
        - INTERVAL '2 months'
    )::date

) AS econ ON TRUE;


-- ============================================================
-- 8. Preview Modeling Dataset
-- ============================================================

SELECT *
FROM vw_modeling_dataset
LIMIT 10;


-- ============================================================
-- 9. Check for Duplicate Sales Keys
-- Run separately during full validation.
-- ============================================================

-- SELECT
--     date,
--     item_id,
--     store_id,
--     COUNT(*) AS row_count
-- FROM vw_modeling_dataset
-- GROUP BY date, item_id, store_id
-- HAVING COUNT(*) > 1;


-- ============================================================
-- 10. Check Missing Values
-- Run separately during full validation.
-- ============================================================

-- SELECT
--     COUNT(*) AS total_rows,
--     COUNT(*) FILTER (
--         WHERE sell_price IS NULL
--     ) AS missing_prices,
--     COUNT(*) FILTER (
--         WHERE temperature_max IS NULL
--     ) AS missing_weather,
--     COUNT(*) FILTER (
--         WHERE unemployment_rate IS NULL
--     ) AS missing_unemployment
-- FROM vw_modeling_dataset;
