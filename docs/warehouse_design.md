# Walmart Enterprise Data Warehouse Design

## Milestone 1.5 — Data Warehouse Design

### Purpose

The Walmart forecasting data warehouse is designed to organize historical sales, pricing, calendar, weather, and economic data into a structured relational model.

The warehouse uses a fact-and-dimension architecture to support:

- Demand forecasting
- Advanced SQL analytics
- Feature engineering
- Pricing analysis
- Revenue optimization
- Business intelligence reporting

## Warehouse Tables

### Dimension Tables

- `dim_calendar` — Calendar dates, Walmart weeks, holidays, events, and SNAP indicators
- `dim_product` — Walmart products, departments, and categories
- `dim_store` — Walmart stores and states
- `dim_economic_series` — Metadata describing external economic indicators

### Fact Tables

- `fact_sales` — Daily product-level sales by store
- `fact_prices` — Weekly product selling prices by store
- `fact_weather` — Daily weather observations by state
- `fact_economic_indicator` — Historical economic indicator observations

## Primary Keys and Foreign Keys

### dim_calendar

**Primary Key**
- `date`

**Important Alternate Key**
- `d`

Used to connect M5 day identifiers such as `d_1`, `d_2`, and `d_3` to actual calendar dates.

---

### dim_product

**Primary Key**
- `item_id`

Used to uniquely identify each Walmart product.

---

### dim_store

**Primary Key**
- `store_id`

Used to uniquely identify each Walmart store.

---

### dim_economic_series

**Primary Key**
- `series_id`

Used to uniquely identify each FRED economic series.

---

### fact_sales

**Composite Business Key**
- `date`
- `item_id`
- `store_id`

**Foreign Key Relationships**
- `date` → `dim_calendar.date`
- `item_id` → `dim_product.item_id`
- `store_id` → `dim_store.store_id`

Each row represents the number of units sold for one product at one store on one date.

---

### fact_prices

**Composite Business Key**
- `store_id`
- `item_id`
- `wm_yr_wk`

**Relationships**
- `store_id` → `dim_store.store_id`
- `item_id` → `dim_product.item_id`
- `wm_yr_wk` → `dim_calendar.wm_yr_wk`

Each row represents the selling price of one product at one store for one Walmart week.

---

### fact_weather

**Composite Business Key**
- `date`
- `state_id`

**Relationships**
- `date` → `dim_calendar.date`
- `state_id` links weather observations to stores through `dim_store.state_id`

Each row represents daily weather conditions for one state.

---

### fact_economic_indicator

**Composite Business Key**
- `series_id`
- `observation_date`

**Foreign Key Relationship**
- `series_id` → `dim_economic_series.series_id`

Each row represents one economic indicator observation for one date.

---

## Table Relationships

The core relationships are:

```text
dim_product
    │
    ├──────────────► fact_sales
    │
    └──────────────► fact_prices

dim_store
    │
    ├──────────────► fact_sales
    │
    └──────────────► fact_prices
    │
    └──────────────► fact_weather
                     through state_id

dim_calendar
    │
    ├──────────────► fact_sales
    │
    ├──────────────► fact_prices
    │                through wm_yr_wk
    │
    └──────────────► fact_weather

dim_economic_series
    │
    └──────────────► fact_economic_indicator

    ## ER Diagram

```mermaid
erDiagram

    DIM_CALENDAR {
        date date PK
        string d
        int wm_yr_wk
        string weekday
        int wday
        int month
        int year
        string event_name_1
        string event_type_1
        string event_name_2
        string event_type_2
        boolean snap_ca
        boolean snap_tx
        boolean snap_wi
    }

    DIM_PRODUCT {
        string item_id PK
        string dept_id
        string cat_id
    }

    DIM_STORE {
        string store_id PK
        string state_id
    }

    DIM_ECONOMIC_SERIES {
        string series_id PK
        string series_name
        string frequency
        string units
    }

    FACT_SALES {
        date date
        string item_id
        string store_id
        int units_sold
    }

    FACT_PRICES {
        string store_id
        string item_id
        int wm_yr_wk
        decimal sell_price
    }

    FACT_WEATHER {
        date date
        string state_id
        decimal temperature_max
        decimal temperature_min
        decimal precipitation
        decimal snowfall
        decimal wind_speed_max
    }

    FACT_ECONOMIC_INDICATOR {
        string series_id
        date observation_date
        decimal value
    }

    DIM_CALENDAR ||--o{ FACT_SALES : date
    DIM_PRODUCT ||--o{ FACT_SALES : item_id
    DIM_STORE ||--o{ FACT_SALES : store_id

    DIM_PRODUCT ||--o{ FACT_PRICES : item_id
    DIM_STORE ||--o{ FACT_PRICES : store_id

    DIM_ECONOMIC_SERIES ||--o{ FACT_ECONOMIC_INDICATOR : series_id