# Walmart Enterprise Demand Forecasting & Decision Intelligence Platform

An end-to-end enterprise-style data engineering, machine learning, demand forecasting, and pricing optimization platform built using the Walmart M5 dataset and dynamic external data sources.

> **Status:** In Development — Data Engineering, Forecasting, and Decision Intelligence Complete; Deployment In Progress

---

# Project Overview

This project demonstrates how a modern retail decision-intelligence platform can be built from raw data ingestion through machine learning and deployment.

The platform combines historical Walmart retail sales and pricing data with external information including weather, economic indicators, holidays, calendar events, and SNAP indicators.

Raw data is processed through Python ETL pipelines, validated through data quality checks, and stored in a PostgreSQL data warehouse. The resulting data is transformed into a machine-learning feature dataset containing millions of product-store-date observations.

Demand forecasting models are then trained using time-based validation. The best-performing model is integrated with a price-elasticity and pricing optimization system that evaluates alternative prices and generates product-level pricing recommendations.

The remaining deployment layer will expose forecasting and pricing results through FastAPI and provide an interactive Streamlit decision-support dashboard.

---

# Objectives

- Build an enterprise-style retail ETL pipeline
- Design and populate a PostgreSQL data warehouse
- Integrate static and dynamic data sources
- Automate data workflows using Apache Airflow
- Implement data quality validation
- Engineer time-series and retail forecasting features
- Train and compare demand forecasting approaches
- Evaluate models using time-based validation
- Estimate product-level price elasticity
- Simulate alternative pricing scenarios
- Generate revenue-oriented pricing recommendations
- Apply realistic pricing guardrails
- Deploy results through a FastAPI service
- Build an interactive Streamlit dashboard
- Containerize application components with Docker

---

# High-Level Architecture

```text
Walmart M5 Dataset
Open-Meteo Weather API
FRED Economic Data
US Holiday Calendar
        │
        ▼
Apache Airflow
        │
        ▼
Python ETL Pipeline
        │
        ▼
Data Quality Validation
        │
        ▼
PostgreSQL Data Warehouse
        │
        ▼
SQL Analytics
        │
        ▼
Feature Engineering
        │
        ▼
Demand Forecasting
        │
        ▼
Price Elasticity Estimation
        │
        ▼
Pricing Optimization
        │
        ▼
FastAPI
        │
        ▼
Streamlit Dashboard
        │
        ▼
Docker
```

---

# Data Sources

## Walmart M5 Dataset

Historical Walmart retail data provides:

- Daily unit sales
- Store identifiers
- Product identifiers
- Departments
- Categories
- Selling prices
- Calendar information
- SNAP indicators
- Events and holidays

## External Data

### Open-Meteo Weather API

Weather features include variables such as:

- Maximum temperature
- Minimum temperature
- Precipitation
- Snowfall
- Maximum wind speed

### FRED Economic Data

Economic indicators include:

- Consumer Price Index (CPI)
- Unemployment rate
- Federal funds rate

### US Holiday Calendar

Holiday and calendar information is incorporated to help capture changes in consumer demand around important dates.

---

# Technology Stack

## Data Engineering

- Python
- Pandas
- NumPy
- PostgreSQL
- SQLAlchemy
- Apache Airflow

## Database & Analytics

- PostgreSQL
- SQL
- Common Table Expressions (CTEs)
- Window Functions
- Views
- Indexes

## Machine Learning

- scikit-learn
- Linear Regression
- Histogram Gradient Boosting
- Time-Based Train/Test Validation
- MAE
- RMSE
- Permutation Feature Importance

## Decision Intelligence

- Price-Demand Analysis
- Price Elasticity Estimation
- Log-Log Elasticity Modeling
- Price Simulation
- Revenue Optimization
- Pricing Guardrails

## Deployment

- FastAPI
- Streamlit
- Docker

## Version Control

- Git
- GitHub

---

# Repository Structure

```text
walmart-enterprise-demand-forecasting/

├── airflow/
│   └── dags/
│
├── api/
│
├── dashboard/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── database/
│
├── docker/
│
├── docs/
│
├── etl/
│   ├── extract/
│   ├── transform/
│   ├── quality/
│   └── load/
│
├── models/
│
├── notebooks/
│
├── sql/
│
├── tests/
│
├── .gitignore
├── docker-compose.yml
├── README.md
└── requirements.txt
```

---

# Data Engineering Pipeline

The project implements an end-to-end data engineering workflow that prepares multiple retail and external data sources for analytics and machine learning.

The pipeline performs:

1. Data extraction from static datasets and external APIs
2. Data validation and quality checks
3. Data transformation
4. Loading into PostgreSQL
5. Integration of sales, pricing, calendar, weather, and economic information
6. Feature engineering for forecasting

The resulting machine-learning dataset contains approximately **4.75 million observations and 30 columns**.

---

# Feature Engineering

The forecasting dataset contains features designed to capture historical demand, trends, calendar patterns, pricing behavior, weather conditions, and economic conditions.

Examples include:

### Historical Demand

- `lag_1`
- `lag_7`
- `lag_30`
- `rolling_avg_7`
- `rolling_avg_28`

### Sales Dynamics

- Short-term sales changes
- Longer-term sales changes

### Calendar

- Day of week
- Day of month
- Month
- Weekend indicator
- Event indicator
- SNAP indicator

### Pricing

- Selling price

### Weather

- Maximum temperature
- Minimum temperature
- Precipitation
- Snowfall
- Maximum wind speed

### Economic

- CPI
- Unemployment rate
- Federal funds rate

---

# Demand Forecasting

The forecasting system uses a chronological train/test split rather than a random split to better represent a real-world forecasting scenario.

The final **28 days** of the dataset are reserved for testing.

### Training Period

February 28, 2011 through April 24, 2016

### Test Period

April 25, 2016 through May 22, 2016

### Models Evaluated

- 28-Day Rolling Average Baseline
- Linear Regression
- Histogram Gradient Boosting

---

# Model Performance

| Model | MAE | RMSE |
|---|---:|---:|
| Histogram Gradient Boosting | 1.0882 | 2.0327 |
| Linear Regression | 1.1253 | 2.1310 |
| Rolling Average Baseline | 1.1288 | 2.1931 |

Histogram Gradient Boosting produced the best performance.

Compared with the baseline model, it achieved approximately:

- **3.60% improvement in MAE**
- **7.32% improvement in RMSE**

The final forecasting model was saved for reuse by downstream pricing and deployment components.

---

# Feature Importance

Permutation feature importance was used to analyze which variables contributed most strongly to demand forecasting performance.

The strongest features included:

1. `rolling_avg_7`
2. `rolling_avg_28`
3. `lag_1`
4. `day_of_week`
5. `lag_7`

Historical demand therefore represents the strongest predictive signal in the current forecasting model.

Pricing, calendar, event, SNAP, weather, and other external variables provide additional contextual information.

---

# Price Elasticity Analysis

Historical price and demand observations are used to estimate product-level price elasticity.

A log-log relationship is used to approximate the percentage change in demand associated with a percentage change in price.

After filtering unstable or implausible estimates:

- **2,163 initial product elasticity estimates**
- **1,048 retained valid elasticity estimates**
- **48.45% of initial estimates retained**

The retained elasticity estimates have an average of approximately:

**-1.19**

This indicates that, across the retained product sample, demand generally decreases as price increases.

---

# Pricing Optimization Engine

The decision-intelligence layer combines:

- Forecasted baseline demand
- Current selling price
- Product-level price elasticity
- Candidate pricing scenarios
- Pricing guardrails
- Revenue calculations

For each eligible product, the system evaluates alternative prices around the current selling price.

Demand is adjusted using estimated price elasticity, and projected revenue is calculated for each scenario.

The system then selects the candidate price with the highest projected revenue while respecting pricing constraints.

---

# Pricing Guardrails

To prevent unrealistic recommendations, candidate prices are constrained to a limited range around the current selling price.

The current implementation limits recommended price movements to approximately:

**±10% of the current selling price**

This creates a more conservative pricing strategy suitable for decision-support experimentation.

---

# Pricing Recommendation Results

The elasticity-aware pricing engine successfully generated recommendations for:

**1,048 products**

Summary results:

| Metric | Result |
|---|---:|
| Products analyzed | 1,048 |
| Average current price | $4.44 |
| Average recommended price | $4.45 |
| Average price change | -0.21% |
| Average elasticity | -1.19 |
| Average projected revenue improvement | 4.43% |
| Price increases | 492 |
| Price decreases | 542 |
| No price change | 14 |

The mix of increases and decreases demonstrates that the optimization engine does not apply a single pricing strategy across all products. Recommendations vary according to each product's estimated demand response.

Projected revenue improvements are model-based simulation results and should not be interpreted as causal estimates of the revenue that would be realized in production.

---

# Generated Machine Learning Artifacts

The project currently produces reusable artifacts including:

```text
data/processed/walmart_features.pkl
data/processed/forecast_predictions.pkl
data/processed/elasticity_pricing_recommendations.pkl

models/gradient_boosting_forecast_model.pkl
```

These artifacts allow downstream applications to use forecasting and pricing results without retraining the model every time.

---

# Roadmap

## Phase 0 — Project Initialization

- [x] Repository setup
- [x] Folder structure
- [x] Business Requirements Document

---

## Phase 1 — Data Engineering

- [x] Data Acquisition
- [x] Data Dictionary
- [x] Exploratory Data Analysis
- [x] Data Warehouse Design
- [x] PostgreSQL Warehouse
- [x] ETL Pipeline
- [x] Data Quality Validation
- [x] External Data Integration
- [x] Airflow Environment / Pipeline Setup

---

## Phase 2 — Analytics & Forecasting

- [x] SQL Analytics
- [x] Feature Engineering
- [x] Time-Based Train/Test Split
- [x] Baseline Forecast
- [x] Linear Regression
- [x] Gradient Boosting Model
- [x] Model Evaluation
- [x] Forecast Visualization
- [x] Forecast Error Analysis
- [x] Permutation Feature Importance
- [x] Save Final Forecasting Model
- [x] Save Forecast Results

---

## Phase 3 — Decision Intelligence

- [x] Price-Demand Analysis
- [x] Product Price Elasticity Estimation
- [x] Elasticity Validation
- [x] Candidate Price Simulation
- [x] Demand Adjustment Using Elasticity
- [x] Revenue Optimization
- [x] Pricing Guardrails
- [x] Product-Level Price Recommendations
- [x] Save Final Pricing Recommendations

---

## Phase 4 — Deployment

- [ ] FastAPI Service
- [ ] Forecasting Endpoints
- [ ] Pricing Recommendation Endpoints
- [ ] Streamlit Dashboard
- [ ] API / Dashboard Integration
- [ ] Docker Integration
- [ ] End-to-End Testing

---

## Phase 5 — Documentation & Portfolio

- [ ] Final Architecture Diagram
- [ ] ER Diagram
- [x] Data Dictionary
- [ ] API Documentation
- [ ] Technical Documentation
- [ ] Dashboard Screenshots
- [ ] Final Project Report
- [ ] Final GitHub Cleanup

---

# Skills Demonstrated

- Enterprise-Style Data Engineering
- Python ETL Development
- PostgreSQL Data Warehousing
- Apache Airflow
- Data Quality Validation
- SQL Analytics
- Multi-Source Data Integration
- Feature Engineering
- Machine Learning
- Demand Forecasting
- Time-Based Model Validation
- Model Evaluation
- Feature Importance
- Price Elasticity Analysis
- Pricing Simulation
- Revenue Optimization
- Decision Intelligence
- Model Serialization
- API Development
- Dashboard Development
- Docker Containerization
- Git Version Control

---

# Disclaimer

This project is an independent educational portfolio project.

It uses the publicly available Walmart M5 forecasting dataset and publicly accessible external data sources. It is not affiliated with, sponsored by, or endorsed by Walmart.

Pricing recommendations and projected revenue improvements are outputs of an experimental modeling and simulation framework and are not actual Walmart pricing recommendations or realized financial results.

---

# Project Status

**Current Milestone: Phase 4 — Deployment**

Completed:

**Data Engineering → Feature Engineering → Demand Forecasting → Price Elasticity → Pricing Optimization**

Next:

**FastAPI → Streamlit → Docker Integration → Final Testing → Documentation**