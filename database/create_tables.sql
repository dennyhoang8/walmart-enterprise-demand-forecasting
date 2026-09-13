-- =====================================================
-- Walmart Enterprise Demand Forecasting Platform
-- PostgreSQL Warehouse Schema
-- =====================================================

DROP TABLE IF EXISTS fact_economic_indicator;
DROP TABLE IF EXISTS dim_economic_series;
DROP TABLE IF EXISTS fact_weather;
DROP TABLE IF EXISTS fact_prices;
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_calendar;
DROP TABLE IF EXISTS dim_store;
DROP TABLE IF EXISTS dim_product;

-- =====================================================
-- Dimension: Product
-- =====================================================

CREATE TABLE dim_product (
    item_id VARCHAR(30) PRIMARY KEY,
    dept_id VARCHAR(20) NOT NULL,
    cat_id VARCHAR(20) NOT NULL
);

-- =====================================================
-- Dimension: Store
-- =====================================================

CREATE TABLE dim_store (
    store_id VARCHAR(10) PRIMARY KEY,
    state_id VARCHAR(5) NOT NULL
);

-- =====================================================
-- Dimension: Calendar
-- =====================================================

CREATE TABLE dim_calendar (
    date DATE PRIMARY KEY,
    d VARCHAR(10) UNIQUE NOT NULL,
    wm_yr_wk INTEGER NOT NULL,
    weekday VARCHAR(10) NOT NULL,
    wday SMALLINT NOT NULL,
    month SMALLINT NOT NULL,
    year SMALLINT NOT NULL,
    event_name_1 VARCHAR(50),
    event_type_1 VARCHAR(30),
    event_name_2 VARCHAR(50),
    event_type_2 VARCHAR(30),
    snap_ca BOOLEAN NOT NULL,
    snap_tx BOOLEAN NOT NULL,
    snap_wi BOOLEAN NOT NULL,

    CONSTRAINT chk_calendar_wday
        CHECK (wday BETWEEN 1 AND 7),

    CONSTRAINT chk_calendar_month
        CHECK (month BETWEEN 1 AND 12)
);

-- =====================================================
-- Fact: Sales
-- =====================================================

CREATE TABLE fact_sales (
    date DATE NOT NULL,
    item_id VARCHAR(30) NOT NULL,
    store_id VARCHAR(10) NOT NULL,
    units_sold INTEGER NOT NULL,

    PRIMARY KEY (date, item_id, store_id),

    CONSTRAINT fk_sales_date
        FOREIGN KEY (date)
        REFERENCES dim_calendar(date),

    CONSTRAINT fk_sales_item
        FOREIGN KEY (item_id)
        REFERENCES dim_product(item_id),

    CONSTRAINT fk_sales_store
        FOREIGN KEY (store_id)
        REFERENCES dim_store(store_id),

    CONSTRAINT chk_units_sold_nonnegative
        CHECK (units_sold >= 0)
);

-- =====================================================
-- Fact: Prices
-- =====================================================

CREATE TABLE fact_prices (
    store_id VARCHAR(10) NOT NULL,
    item_id VARCHAR(30) NOT NULL,
    wm_yr_wk INTEGER NOT NULL,
    sell_price NUMERIC(10, 2) NOT NULL,

    PRIMARY KEY (store_id, item_id, wm_yr_wk),

    CONSTRAINT fk_prices_store
        FOREIGN KEY (store_id)
        REFERENCES dim_store(store_id),

    CONSTRAINT fk_prices_item
        FOREIGN KEY (item_id)
        REFERENCES dim_product(item_id),

    CONSTRAINT chk_sell_price_positive
        CHECK (sell_price > 0)
);

-- =====================================================
-- Fact: Weather
-- =====================================================

CREATE TABLE fact_weather (
    date DATE NOT NULL,
    state_id VARCHAR(5) NOT NULL,
    temperature_max NUMERIC(6, 2),
    temperature_min NUMERIC(6, 2),
    precipitation NUMERIC(8, 2),
    snowfall NUMERIC(8, 2),
    wind_speed_max NUMERIC(6, 2),

    PRIMARY KEY (date, state_id),

    CONSTRAINT fk_weather_date
        FOREIGN KEY (date)
        REFERENCES dim_calendar(date),

    CONSTRAINT chk_precipitation_nonnegative
        CHECK (precipitation IS NULL OR precipitation >= 0),

    CONSTRAINT chk_snowfall_nonnegative
        CHECK (snowfall IS NULL OR snowfall >= 0)
);

-- =====================================================
-- Dimension: Economic Series
-- =====================================================

CREATE TABLE dim_economic_series (
    series_id VARCHAR(30) PRIMARY KEY,
    series_name VARCHAR(100) NOT NULL,
    frequency VARCHAR(20) NOT NULL,
    units VARCHAR(50)
);

-- =====================================================
-- Fact: Economic Indicators
-- =====================================================

CREATE TABLE fact_economic_indicator (
    series_id VARCHAR(30) NOT NULL,
    observation_date DATE NOT NULL,
    value NUMERIC(18, 6),

    PRIMARY KEY (series_id, observation_date),

    CONSTRAINT fk_economic_series
        FOREIGN KEY (series_id)
        REFERENCES dim_economic_series(series_id)
);

-- =====================================================
-- Indexes
-- =====================================================

CREATE INDEX idx_calendar_wm_yr_wk
    ON dim_calendar(wm_yr_wk);

CREATE INDEX idx_sales_item_date
    ON fact_sales(item_id, date);

CREATE INDEX idx_sales_store_date
    ON fact_sales(store_id, date);

CREATE INDEX idx_sales_date
    ON fact_sales(date);

CREATE INDEX idx_prices_item_store_week
    ON fact_prices(item_id, store_id, wm_yr_wk);

CREATE INDEX idx_weather_state_date
    ON fact_weather(state_id, date);

CREATE INDEX idx_economic_observation_date
    ON fact_economic_indicator(observation_date);