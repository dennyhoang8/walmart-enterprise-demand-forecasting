# Walmart M5 Data Dictionary

## 1. calendar.csv

| Column | Data Type | Description | Example | Nullable | Business Meaning |
|---|---|---|---|---|---|
| date | Date | Calendar date | 2011-01-29 | No | Actual date linked to each sales day |
| wm_yr_wk | Integer | Walmart year-week identifier | 11101 | No | Connects calendar dates to weekly selling prices |
| weekday | String | Name of the weekday | Saturday | No | Useful for weekly seasonality |
| wday | Integer | Numeric weekday identifier | 1 | No | Encoded weekday |
| month | Integer | Calendar month | 1 | No | Monthly seasonality |
| year | Integer | Calendar year | 2011 | No | Annual grouping |
| d | String | Sales-day identifier | d_1 | No | Connects calendar data to sales columns |
| event_name_1 | String | Primary event or holiday | SuperBowl | Yes | First event affecting demand |
| event_type_1 | String | Type of primary event | Sporting | Yes | Category of the first event |
| event_name_2 | String | Secondary event or holiday | Easter | Yes | Second event on the same date |
| event_type_2 | String | Type of secondary event | Religious | Yes | Category of the second event |
| snap_CA | Integer | SNAP eligibility flag for California | 0 | No | Indicates SNAP purchase eligibility |
| snap_TX | Integer | SNAP eligibility flag for Texas | 1 | No | Indicates SNAP purchase eligibility |
| snap_WI | Integer | SNAP eligibility flag for Wisconsin | 0 | No | Indicates SNAP purchase eligibility |

## 2. sell_prices.csv

| Column | Data Type | Description | Example | Nullable | Business Meaning |
|---|---|---|---|---|---|
| store_id | String | Store identifier | CA_1 | No | Identifies the Walmart store |
| item_id | String | Product identifier | HOBBIES_1_001 | No | Identifies the product |
| wm_yr_wk | Integer | Walmart year-week identifier | 11325 | No | Connects weekly prices to calendar dates |
| sell_price | Decimal | Weekly selling price | 9.58 | No | Historical selling price for the product |

## 3. sales_train_validation.csv

| Column | Data Type | Description | Example | Nullable | Business Meaning |
|---|---|---|---|---|---|
| id | String | Unique product-store series identifier | HOBBIES_1_001_CA_1_validation | No | Unique time-series key |
| item_id | String | Product identifier | HOBBIES_1_001 | No | Identifies the product |
| dept_id | String | Department identifier | HOBBIES_1 | No | Product department |
| cat_id | String | Category identifier | HOBBIES | No | Product category |
| store_id | String | Store identifier | CA_1 | No | Store where sales occurred |
| state_id | String | State identifier | CA | No | State where the store is located |
| d_1 to d_1913 | Integer | Daily unit sales | 0 | No | Number of units sold on each day |

## 4. sales_train_evaluation.csv

Same structure as `sales_train_validation.csv`, but it contains additional sales-day columns for the evaluation period.

## 5. sample_submission.csv

| Column | Data Type | Description | Example | Nullable | Business Meaning |
|---|---|---|---|---|---|
| id | String | Forecast series identifier | HOBBIES_1_001_CA_1_validation | No | Identifies the product-store forecast series |
| F1 to F28 | Decimal | Forecast values for the next 28 days | 0 | No | Predicted unit sales for each future day |

## 6. Relationships

- `calendar.d` connects to the daily columns in the sales tables.
- `calendar.wm_yr_wk` connects to `sell_prices.wm_yr_wk`.
- `sales.item_id` connects to `sell_prices.item_id`.
- `sales.store_id` connects to `sell_prices.store_id`.
- Each sales row represents one item sold at one store over time.

## 7. dim_calendar

| Column | Data Type | Description | Nullable | Business Meaning |
|---|---|---|---|---|
| date | Date | Calendar date | No | Primary calendar date used for time-based analysis |
| d | String | M5 day identifier | No | Links M5 sales days to calendar dates |
| wm_yr_wk | Integer | Walmart year-week identifier | No | Links calendar dates to weekly product prices |
| weekday | String | Weekday name | No | Supports weekly seasonality analysis |
| wday | Small Integer | Numeric weekday | No | Encoded weekday |
| month | Small Integer | Calendar month | No | Supports monthly seasonality |
| year | Small Integer | Calendar year | No | Supports yearly analysis |
| event_name_1 | String | Primary event or holiday | Yes | Identifies events that may affect demand |
| event_type_1 | String | Primary event category | Yes | Classifies the primary event |
| event_name_2 | String | Secondary event | Yes | Identifies an additional event on the same date |
| event_type_2 | String | Secondary event category | Yes | Classifies the secondary event |
| snap_ca | Boolean | California SNAP indicator | No | Indicates California SNAP participation date |
| snap_tx | Boolean | Texas SNAP indicator | No | Indicates Texas SNAP participation date |
| snap_wi | Boolean | Wisconsin SNAP indicator | No | Indicates Wisconsin SNAP participation date |

---

## 8. dim_economic_series

| Column | Data Type | Description | Nullable | Business Meaning |
|---|---|---|---|---|
| series_id | String | Economic series identifier | No | Identifies the FRED economic indicator |
| series_name | String | Economic series name | No | Human-readable economic indicator name |
| frequency | String | Observation frequency | No | Indicates how frequently the series is reported |
| units | String | Measurement units | Yes | Describes the units of the economic value |

---

## 9. dim_product

| Column | Data Type | Description | Nullable | Business Meaning |
|---|---|---|---|---|
| item_id | String | Walmart product identifier | No | Uniquely identifies a product |
| dept_id | String | Department identifier | No | Groups products into departments |
| cat_id | String | Category identifier | No | Groups products into major categories |

---

## 10. dim_store

| Column | Data Type | Description | Nullable | Business Meaning |
|---|---|---|---|---|
| store_id | String | Walmart store identifier | No | Uniquely identifies a store |
| state_id | String | State identifier | No | Identifies the state containing the store |

---

## 11. fact_sales

| Column | Data Type | Description | Nullable | Business Meaning |
|---|---|---|---|---|
| date | Date | Date of sales observation | No | Identifies when the sales occurred |
| item_id | String | Product identifier | No | Identifies the product sold |
| store_id | String | Store identifier | No | Identifies where the sale occurred |
| units_sold | Integer | Number of units sold | No | Primary demand variable used for forecasting |

---

## 12. fact_prices

| Column | Data Type | Description | Nullable | Business Meaning |
|---|---|---|---|---|
| store_id | String | Store identifier | No | Identifies the store offering the product |
| item_id | String | Product identifier | No | Identifies the priced product |
| wm_yr_wk | Integer | Walmart year-week identifier | No | Identifies the week for the recorded price |
| sell_price | Numeric | Product selling price | No | Historical product price used for pricing and demand analysis |

---

## 13. fact_economic_indicator

| Column | Data Type | Description | Nullable | Business Meaning |
|---|---|---|---|---|
| series_id | String | Economic series identifier | No | Links the observation to an economic indicator |
| observation_date | Date | Date of economic observation | No | Identifies when the economic value was measured |
| value | Numeric | Economic indicator value | Yes | Provides external economic context for demand forecasting |

---

## 14. fact_weather

| Column | Data Type | Description | Nullable | Business Meaning |
|---|---|---|---|---|
| date | Date | Weather observation date | No | Links weather conditions to sales dates |
| state_id | String | State identifier | No | Associates weather with Walmart store locations |
| temperature_max | Numeric | Maximum daily temperature | Yes | Captures potential temperature effects on demand |
| temperature_min | Numeric | Minimum daily temperature | Yes | Captures potential temperature effects on demand |
| precipitation | Numeric | Daily precipitation | Yes | Measures rain/precipitation conditions |
| snowfall | Numeric | Daily snowfall | Yes | Measures snowfall conditions |
| wind_speed_max | Numeric | Maximum daily wind speed | Yes | Captures severe or unusual weather conditions |

---

## 15. Warehouse Relationships

- `fact_sales.item_id` → `dim_product.item_id`
- `fact_sales.store_id` → `dim_store.store_id`
- `fact_sales.date` → `dim_calendar.date`
- `fact_prices.item_id` → `dim_product.item_id`
- `fact_prices.store_id` → `dim_store.store_id`
- `fact_prices.wm_yr_wk` → `dim_calendar.wm_yr_wk`
- `fact_weather.state_id` → `dim_store.state_id`
- `fact_weather.date` → `dim_calendar.date`
- `fact_economic_indicator.series_id` → `dim_economic_series.series_id`

The warehouse separates descriptive dimension tables from high-volume fact tables, supporting scalable SQL analytics, feature engineering, and demand forecasting.