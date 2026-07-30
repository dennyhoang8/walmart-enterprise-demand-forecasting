# Business Requirements Document

# Walmart Enterprise Demand Forecasting and Pricing Platform

## 1. Project Overview

This project develops a production-style retail data platform using the publicly available Walmart M5 forecasting dataset and continuously updated external data sources.

The platform will combine historical Walmart sales and pricing data with weather, holidays, and economic indicators. The resulting data will be stored in a PostgreSQL data warehouse and used to forecast future product demand.

The project will also explore pricing scenarios by estimating expected demand and revenue at different proposed prices.

The final system will include automated data ingestion, data transformation, feature engineering, machine learning, an inference API, an interactive dashboard, and containerized deployment.

## 2. Business Problem

Large retailers must determine how much product demand to expect across thousands of products, stores, and dates.

Demand can change because of factors such as:

- Product price
- Promotions
- Holidays
- Seasonal patterns
- Store location
- Weather
- Inflation
- Economic conditions
- Historical purchasing behavior

Inaccurate forecasts may lead to:

- Product stockouts
- Excess inventory
- Storage costs
- Lost revenue
- Poor pricing decisions
- Inefficient supply-chain planning

The business needs an automated system that combines historical and continuously updated data to produce timely demand forecasts and pricing recommendations.

## 3. Project Goal

Build an end-to-end retail demand forecasting platform that:

- Ingests static and dynamic data
- Cleans and validates incoming data
- Stores structured data in PostgreSQL
- Automates ingestion using Apache Airflow
- Creates time-series and pricing features
- Predicts future product demand
- Evaluates potential pricing scenarios
- Serves predictions through FastAPI
- Displays results through Streamlit
- Runs through Docker containers

## 4. Stakeholders

The primary stakeholders are:

- Executive Leadership
- Pricing and Revenue Management Team
- Supply Chain Team
- Inventory Planning Team
- Merchandising Team
- Store Managers
- Finance Team
- Data Engineering Team
- Data Science Team
- Machine Learning Engineering Team

## 5. Business Objectives

The main business objectives are:

1. Improve product-demand forecasting.
2. Support inventory and supply-chain planning.
3. Identify seasonal and holiday-driven demand patterns.
4. Measure the relationship between price and product demand.
5. Estimate revenue under different pricing scenarios.
6. automate the collection of external business data.
7. Create a centralized retail data warehouse.
8. Make forecasts accessible through an API and dashboard.

## 6. Key Performance Indicators

### Business KPIs

- Units Sold
- Sales Revenue
- Average Selling Price
- Product Demand Growth
- Store Sales Growth
- Category Sales Growth
- Promotion Lift
- Estimated Revenue at Recommended Price

### Forecasting KPIs

- Mean Absolute Error
- Root Mean Squared Error
- Mean Absolute Percentage Error
- Weighted Root Mean Squared Scaled Error
- Forecast Bias

### Data Engineering KPIs

- Pipeline Success Rate
- Data Freshness
- Records Processed
- Duplicate Rate
- Missing-Value Rate
- Data Validation Failure Rate
- ETL Runtime

## 7. Success Metrics

The project will be considered successful when:

- Walmart M5 data is loaded into a structured PostgreSQL warehouse.
- Dynamic external data is collected automatically.
- Airflow successfully executes the ingestion pipeline.
- Data-quality checks detect missing or invalid records.
- Forecasting models outperform a simple baseline forecast.
- The system returns demand predictions through FastAPI.
- The dashboard displays forecasts, pricing scenarios, and pipeline status.
- The complete system can run using Docker Compose.
- The project is documented clearly enough for another person to reproduce it.

## 8. Project Scope

### In Scope

- Public Walmart M5 data
- Weather data
- Holiday data
- CPI and inflation-related data
- Historical sales analysis
- Historical selling-price analysis
- PostgreSQL data warehouse
- Python ETL scripts
- Apache Airflow orchestration
- SQL and Pandas feature engineering
- Demand forecasting
- Pricing-scenario analysis
- FastAPI
- Streamlit
- Docker
- GitHub documentation

### Out of Scope

- Access to Walmart internal systems
- Private Walmart customer data
- Private Walmart inventory data
- Real-time modification of Walmart prices
- Production deployment inside Walmart
- Claims that the project represents an official Walmart system
- Guaranteed causal price-elasticity estimates
- Autonomous business decisions without human review

## 9. Data Sources

### Static Data

The Walmart M5 dataset will provide:

- Historical daily unit sales
- Product identifiers
- Product departments
- Product categories
- Store identifiers
- State identifiers
- Historical weekly selling prices
- Calendar dates
- Events and holidays
- SNAP indicators

### Dynamic Data

External data sources may include:

- Weather API data
- Consumer Price Index
- Inflation indicators
- Unemployment indicators
- Interest-rate indicators
- U.S. holiday data

## 10. High-Level Architecture

The system will follow this workflow:

Static and Dynamic Data Sources

↓

Apache Airflow ETL Pipeline

↓

PostgreSQL Data Warehouse

↓

SQL and Pandas Feature Engineering

↓

Demand Forecasting Models

↓

Pricing Scenario and Revenue Optimization Engine

↓

FastAPI Prediction Service

↓

Streamlit Dashboard

↓

Docker Deployment

## 11. Assumptions

- The M5 dataset represents historical Walmart sales but not Walmart's complete modern enterprise data.
- External data may use different frequencies from the daily sales data.
- Economic indicators may be monthly or weekly rather than daily.
- Some pricing and promotion behavior must be inferred from available fields.
- The project is educational and portfolio-focused.
- Forecasting accuracy may differ by product, store, and forecast horizon.
- Pricing recommendations are analytical scenarios rather than actual Walmart business decisions.

## 12. Risks and Limitations

- The historical dataset does not update continuously.
- Dynamic external data occurs after the M5 historical period.
- Historical weather may require separate backfilling.
- Correlation does not establish causation.
- Price-elasticity estimates may be biased by promotions and other variables.
- Large datasets may require memory-efficient processing.
- Airflow and Docker may create setup complexity.
- Forecast accuracy may be poor for products with intermittent demand.
- The system may require aggregation or sampling during early development.

## 13. Planned Deliverables

- Business Requirements Document
- Data Dictionary
- Data Understanding Notebook
- Entity Relationship Diagram
- PostgreSQL Database
- ETL Scripts
- Airflow DAGs
- Data Quality Checks
- SQL Feature Views
- Forecasting Models
- Model Evaluation Report
- Pricing Scenario Engine
- FastAPI Application
- Streamlit Dashboard
- Docker Compose Environment
- Architecture Diagram
- Final README