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