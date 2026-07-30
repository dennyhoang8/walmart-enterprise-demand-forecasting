# 🛒 Walmart Enterprise Demand Forecasting & Decision Intelligence Platform

An end-to-end enterprise data engineering and machine learning project that forecasts retail demand and simulates pricing decisions using the Walmart M5 dataset and dynamic external data sources.

> **Status:** 🚧 In Development (Phase 1 – Data Engineering)

---

# Project Overview

This project demonstrates how a modern retail analytics platform can be built from raw data ingestion through deployment.

The platform combines historical Walmart retail sales with continuously updated external data such as weather, economic indicators, and holidays. The data is processed through automated ETL pipelines, stored in a PostgreSQL data warehouse, transformed into predictive features, and used to forecast demand and evaluate pricing scenarios.

The final system exposes predictions through a FastAPI service and visualizes business insights using a Streamlit dashboard.

---

# Objectives

- Build an enterprise-style ETL pipeline
- Design a PostgreSQL data warehouse
- Automate data ingestion using Apache Airflow
- Implement data quality validation
- Engineer forecasting features
- Compare multiple forecasting models
- Simulate pricing scenarios
- Deploy a prediction API
- Build an executive dashboard
- Containerize the entire application with Docker

---

# High-Level Architecture

```
Real Data Sources
        │
        ▼
Apache Airflow ETL
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
Advanced SQL Analytics
        │
        ▼
Feature Engineering
        │
        ▼
Forecasting Models
        │
        ▼
Decision Intelligence
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

## Static Data

- Walmart M5 Forecasting Dataset

## Dynamic Data

- Open-Meteo Weather API
- FRED Economic API
- US Holiday Calendar

---

# Technology Stack

## Data Engineering

- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- Apache Airflow

## SQL

- PostgreSQL
- Common Table Expressions (CTEs)
- Window Functions
- Views
- Indexes

## Machine Learning

- scikit-learn
- Random Forest
- XGBoost
- LightGBM
- Prophet
- SARIMAX

## Deployment

- FastAPI
- Streamlit
- Docker

## Version Control

- Git
- GitHub

---

# Repository Structure

```
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

# Roadmap

## Phase 0 — Project Initialization

- [x] Repository setup
- [x] Folder structure
- [x] Business Requirements Document

---

## Phase 1 — Data Engineering

- [ ] Data Acquisition
- [ ] Data Dictionary
- [ ] Exploratory Data Analysis
- [ ] Data Warehouse Design
- [ ] PostgreSQL Warehouse
- [ ] ETL Pipeline
- [ ] Airflow Automation

---

## Phase 2 — Analytics & Forecasting

- [ ] Advanced SQL Analytics
- [ ] Feature Engineering
- [ ] Baseline Models
- [ ] Machine Learning Models
- [ ] Time-Series Models
- [ ] Model Evaluation

---

## Phase 3 — Decision Intelligence

- [ ] Price Simulation
- [ ] Revenue Optimization
- [ ] Business Insights

---

## Phase 4 — Deployment

- [ ] FastAPI
- [ ] Streamlit Dashboard
- [ ] Docker Deployment

---

## Phase 5 — Documentation

- [ ] Architecture Diagram
- [ ] ER Diagram
- [ ] Data Dictionary
- [ ] API Documentation
- [ ] Technical Design
- [ ] Final Report

---

# Skills Demonstrated

- Enterprise Data Engineering
- ETL Development
- Data Warehousing
- Data Quality Validation
- Advanced SQL
- Feature Engineering
- Machine Learning
- Time-Series Forecasting
- Decision Intelligence
- Revenue Optimization
- API Development
- Dashboard Development
- Docker Containerization

---

# Disclaimer

This project is an independent educational portfolio project.

It uses the publicly available Walmart M5 forecasting dataset and publicly accessible external data sources. It is not affiliated with, sponsored by, or endorsed by Walmart.

---

# Project Status

🚧 **Current Milestone:** Phase 1 — Data Acquisition