# Walmart Enterprise Demand Forecasting & Dynamic Pricing

An end-to-end data science and machine learning project that simulates an enterprise retail forecasting and pricing system using Walmart's M5 dataset.

The project builds a complete pipeline from raw data ingestion and validation through feature engineering, demand forecasting, dynamic pricing recommendations, API serving, dashboarding, workflow orchestration, and Dockerized deployment.

---

## Project Overview

Retailers need to answer two closely related questions:

1. **How much demand should we expect for a product?**
2. **What price should we recommend given that expected demand?**

This project develops an end-to-end system for addressing both problems.

The system combines historical Walmart sales and pricing data with calendar, holiday, weather, and economic information to create model-ready features.

A machine learning model predicts product demand, while a separate pricing engine evaluates controlled price scenarios and recommends whether a product's price should be increased, decreased, or kept unchanged.

The final system exposes predictions through a **FastAPI backend** and an interactive **Streamlit dashboard**, while **PostgreSQL, Apache Airflow, and Docker** support the surrounding data infrastructure.

---

## System Architecture

```text
                    RAW DATA SOURCES
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   Walmart M5          Weather API          FRED
 Sales / Prices        Open-Meteo       Economic Data
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
                           ▼
                    ETL PIPELINE
             Extract → Validate → Load
                           │
                           ▼
                      PostgreSQL
                           │
                           ▼
                  Feature Engineering
                           │
                           ▼
                  Forecasting Model
                           │
                           ▼
                  Demand Predictions
                           │
                           ▼
                  Dynamic Pricing Engine
                           │
                           ▼
                       FastAPI
                           │
                           ▼
                      Streamlit
                           │
                           ▼
                 Interactive Dashboard


        Airflow → Pipeline Orchestration
        Docker  → Containerized Environment
```

---

## Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn |
| Database | PostgreSQL |
| ORM / Database Access | SQLAlchemy |
| Workflow Orchestration | Apache Airflow |
| API | FastAPI |
| Dashboard | Streamlit |
| Containerization | Docker / Docker Compose |
| Testing | Pytest |
| External Data | Open-Meteo, FRED, U.S. Holidays |

---

## Data Sources

### Walmart M5 Forecasting Dataset

The core retail data comes from Walmart's M5 forecasting dataset.

It contains:

- Historical unit sales
- Product hierarchy
- Store information
- Historical selling prices
- Calendar information
- Events and holidays

The project primarily works with the following files:

```text
calendar.csv
sell_prices.csv
sales_train_validation.csv
sales_train_evaluation.csv
```

### Weather Data

Historical weather data is collected using Open-Meteo for the states represented in the M5 dataset:

```text
California
Texas
Wisconsin
```

### Economic Data

Economic indicators are collected from the Federal Reserve Economic Data (FRED) API.

The project includes:

```text
CPIAUCSL   → Consumer Price Index
UNRATE     → Unemployment Rate
FEDFUNDS   → Federal Funds Rate
```

### Holiday Data

U.S. holiday information is incorporated to help capture demand changes around important calendar events.

---

## ETL Pipeline

The ETL layer extracts external and local data, validates it, and prepares it for downstream analysis.

```text
Extract
   ↓
Validate
   ↓
Load
   ↓
PostgreSQL
```

The project includes separate processes for:

- Walmart sales
- Product prices
- Calendar information
- Weather
- Economic indicators
- Holidays

Data-quality checks are performed before downstream modeling.

Examples include:

- Null key checks
- Duplicate checks
- Date validation
- Schema validation
- Dimension integrity checks

---

## PostgreSQL Data Warehouse

PostgreSQL provides the structured storage layer for the project.

The warehouse includes dimension and fact tables such as:

```text
dim_product
dim_store
dim_calendar
dim_economic_series

fact_sales
fact_prices
fact_weather
```

This separates raw storage and analytical processing from the machine learning layer and better represents how data would be managed in a production analytics environment.

---

## Apache Airflow

Apache Airflow is used to orchestrate the project's data pipeline.

Airflow provides:

- Task scheduling
- Dependency management
- Pipeline monitoring
- Repeatable ETL execution
- Failure visibility

The Airflow scheduler and webserver run as separate Docker services.

---

## Exploratory Data Analysis

The notebook workflow investigates the major components of the retail dataset before modeling.

Analysis includes:

- Sales distributions
- Product and category behavior
- Store-level demand
- Missing values
- Price behavior
- Calendar effects
- Event and holiday effects
- Time-series patterns

The notebooks are designed to move progressively from understanding the raw data toward a production-ready forecasting pipeline.

---

## Feature Engineering

Historical sales and external information are transformed into model-ready features.

Examples include:

### Time Features

```text
day of week
month
year
week
weekend indicators
```

### Lag Features

Historical demand values are shifted backward to provide the model with information about previous sales behavior.

Examples:

```text
lag_7
lag_28
```

### Rolling Features

Rolling statistics summarize recent demand behavior.

Examples include rolling averages and related historical demand measures.

### Calendar Features

Features incorporate:

- Events
- Holidays
- SNAP information
- Calendar structure

### External Features

The feature pipeline can also incorporate:

- Weather
- CPI
- Unemployment
- Federal funds rate

The resulting model-ready feature dataset is used by the forecasting pipeline.

---

## Demand Forecasting

The forecasting component predicts expected unit demand at the product/store/date level.

The final forecasting workflow uses a **Poisson Histogram Gradient Boosting** approach designed for non-negative count-like demand data.

The model learns relationships between historical demand and features such as:

```text
Historical sales
Lagged demand
Rolling demand
Price
Calendar information
Events
Holidays
External variables
```

Predictions are constrained to prevent negative demand forecasts.

---

## Model Evaluation

Forecasting performance is evaluated using time-aware validation rather than randomly mixing past and future observations.

Primary evaluation metrics include:

### MAE — Mean Absolute Error

Measures the average absolute difference between predicted demand and actual demand.

Lower is better.

### RMSE — Root Mean Squared Error

Measures prediction error while penalizing large mistakes more heavily than MAE.

Lower is better.

The forecasting workflow also compares model performance against simpler baseline predictions.

This helps determine whether the machine learning model actually provides additional forecasting value.

---

## Dynamic Pricing Engine

Demand predictions are passed into a scenario-based pricing engine.

The pricing system evaluates controlled price changes and estimates their effect on expected demand and revenue.

For each product/date combination, the system can recommend:

```text
Increase
Decrease
Keep
```

The engine includes price guardrails to prevent unrealistic recommendations.

It also distinguishes between:

```text
Observed elasticity
Fallback elasticity
```

Recommendations must meet minimum simulated revenue-improvement requirements before they are considered actionable.

---

## Pricing Results

During the latest full pricing run:

```text
Pricing recommendations: 326,838

Decrease: 28.24%
Keep:     68.39%
Increase:  3.37%

Actionable recommendations: 101,392
Actionable rate: 31.02%
```

Elasticity sources:

```text
Observed: 103,305
Fallback: 223,533
```

The scenario simulation produced:

```text
Current expected revenue:
$1,202,032.22

Recommended expected revenue:
$1,264,768.32

Simulated revenue lift:
$62,736.10

Simulated revenue lift:
5.22%
```

> **Important:** These results represent model-based scenario simulations, not experimentally verified causal revenue gains.

---

## FastAPI Backend

FastAPI exposes the forecasting and pricing functionality through an API.

The API includes endpoints for:

```text
/health
/forecast
/recommend-price
```

Example architecture:

```text
Client
   ↓
FastAPI
   ↓
Forecasting Model
   ↓
Pricing Engine
   ↓
JSON Response
```

Interactive API documentation is available locally at:

```text
localhost:8000/docs
```

---

## Streamlit Dashboard

The Streamlit application provides a user-friendly interface for interacting with the system.

Users can select:

```text
Item
Store
Date
```

and request a demand forecast.

The dashboard can display:

- Predicted demand
- Current price
- Recommended price
- Pricing action
- Expected demand
- Simulated revenue
- Revenue lift
- Elasticity
- Recommendation status

The local dashboard runs at:

```text
localhost:8501
```

---

## Docker Architecture

The project is containerized with Docker Compose.

The main services are:

```text
PostgreSQL
Airflow Init
Airflow Scheduler
Airflow Webserver
FastAPI
Streamlit
```

Conceptually:

```text
┌─────────────────────┐
│      Streamlit      │
│       :8501         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│       FastAPI       │
│        :8000        │
└─────────────────────┘

┌─────────────────────┐
│      PostgreSQL     │
│   Host port :5433   │
└─────────────────────┘

┌─────────────────────┐
│       Airflow       │
│        :8080        │
└─────────────────────┘
```

Docker provides a reproducible environment for running the infrastructure and application services.

---

## Running the Project

### 1. Clone the repository

```bash
git clone <repository-url>
cd walmart-enterprise-demand-forecasting
```

### 2. Configure environment variables

Create a `.env` file containing the required environment variables.

Example:

```text
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=...
FRED_API_KEY=...
```

Do **not** commit the `.env` file to GitHub.

### 3. Build and start Docker

```bash
docker compose up -d --build
```

### 4. Verify containers

```bash
docker compose ps
```

Expected services include:

```text
walmart_postgres
walmart_airflow_scheduler
walmart_airflow_webserver
walmart_api
walmart_streamlit
```

### 5. Open the applications

```text
Streamlit:
localhost:8501

FastAPI:
localhost:8000/docs

Airflow:
localhost:8080
```

### 6. Stop the environment

```bash
docker compose down
```

The PostgreSQL Docker volume persists unless it is explicitly removed.

---

## Automated Testing

The project includes API smoke tests using Pytest.

Tests verify functionality such as:

- API health
- Demand forecast requests
- Pricing recommendations
- Invalid or unavailable forecasting requests

Run tests with:

```bash
python -m pytest tests/test_api_smoke.py -v
```

---

## Project Structure

```text
walmart-enterprise-demand-forecasting/
│
├── airflow/
│   └── dags/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── ...
│
├── docker/
│   ├── Dockerfile.airflow
│   ├── Dockerfile.api
│   └── Dockerfile.streamlit
│
├── etl/
│   ├── extract/
│   ├── load/
│   └── quality/
│
├── models/
│
├── notebooks/
│   ├── 01_...
│   ├── 02_...
│   ├── 03_...
│   ├── 04_...
│   ├── 05_...
│   └── 06_...
│
├── outputs/
│   ├── forecasting/
│   └── pricing/
│
├── src/
│   ├── api/
│   │   └── main.py
│   │
│   ├── dashboard/
│   │   └── app.py
│   │
│   ├── features/
│   │   └── build_features.py
│   │
│   ├── forecasting/
│   │   └── predict.py
│   │
│   └── pricing/
│       └── recommend_price.py
│
├── tests/
│   └── test_api_smoke.py
│
├── .env
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Current Limitations

This project is designed as a portfolio-scale simulation of an enterprise forecasting system rather than a live Walmart production system.

Important limitations include:

- The current API primarily scores model-ready dates available in the processed feature dataset.
- True recursive multi-step future forecasting is not yet implemented.
- Pricing recommendations are scenario-based rather than causal estimates.
- Historical price elasticity can be difficult to estimate for products with limited price variation.
- Fallback elasticity is required when sufficient historical evidence is unavailable.
- Simulated revenue improvement should not be interpreted as guaranteed real-world revenue improvement.
- Production deployment would require additional monitoring, security, scaling, and model-governance infrastructure.

---

## Future Improvements

Potential extensions include:

- Recursive future forecasting
- Automated future feature generation
- Forecast uncertainty intervals
- Stronger product-level elasticity models
- Controlled pricing experiments / A/B testing
- Model drift monitoring
- Automated retraining
- Cloud deployment
- CI/CD
- Authentication and API security
- Additional stores and product coverage
- More extensive hyperparameter optimization

---

## Key Skills Demonstrated

This project demonstrates experience across the full data science lifecycle:

```text
Data ingestion
Data validation
ETL
SQL
PostgreSQL
Exploratory data analysis
Feature engineering
Time-series forecasting
Machine learning
Model evaluation
Dynamic pricing
API development
Dashboard development
Automated testing
Workflow orchestration
Docker
Production-oriented project structure
```

Rather than ending with a notebook and a trained model, the project demonstrates how a machine learning workflow can be connected to the surrounding infrastructure required to turn predictions into a usable application.

---

## Disclaimer

This project is an independent educational and portfolio project using publicly available data.

It is not affiliated with, endorsed by, or deployed by Walmart.

Pricing results are simulated model outputs and should not be interpreted as actual Walmart pricing recommendations or guaranteed financial outcomes.

---

## Author

**Denny Hoang**

M.S. Data Science  
University of St. Thomas