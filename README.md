# 🎬 Netflix User Behavior Data Pipeline

> A batch ETL project built with **Apache Airflow**, **PostgreSQL**, **Docker**, and **Metabase** — processing raw Netflix-style user activity data into analytics-ready datasets using **Medallion Architecture** (Bronze → Silver → Gold).

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Pipeline Architecture](#pipeline-architecture)
- [Airflow DAG](#airflow-dag)
- [Running the Pipeline](#running-the-pipeline)
- [Access Services](#access-services)
- [Data Visualization](#data-visualization)
- [Notes](#notes)
- [Author](#author)

---

## 🧭 Overview

This project simulates a real-world data engineering pipeline for Netflix-style user behavior data. Raw CSV files are ingested, cleaned, and transformed into a star schema ready for analytics and dashboarding.

**Datasets processed:**

| Dataset | Description |
|---|---|
| `users` | User profile data |
| `movies` | Movie metadata |
| `watch_history` | User viewing records |
| `search_logs` | Search activity logs |
| `recommendation_logs` | Recommendation engine logs |
| `reviews` | User review data |

---

## 🛠 Tech Stack

| Tool | Role |
|---|---|
| Apache Airflow | Pipeline orchestration |
| PostgreSQL | Data storage (Bronze / Silver / Gold) |
| Docker & Docker Compose | Containerized environment |
| Metabase | Data visualization & dashboarding |

---

## 🚀 Installation

Make sure **Docker** and **Docker Compose** are installed on your machine.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd netflix-data-engineering
```

### 2. Start All Services

```bash
docker-compose up -d
```

### 3. Create Airflow Admin User

```bash
docker-compose run --rm airflow-webserver airflow users create \
  --username admin \
  --firstname Admin \
  --lastname User \
  --role Admin \
  --email admin@example.com \
  --password admin
```

---

## 🏗 Pipeline Architecture

This pipeline follows the **Medallion Architecture** with three layers:

```
Raw CSV Files
     │
     ▼
┌─────────────┐
│  🥉 BRONZE  │  Load raw data as-is into PostgreSQL
└─────────────┘
     │
     ▼
┌─────────────┐
│  🥈 SILVER  │  Clean, validate, and standardize data
└─────────────┘
     │
     ▼
┌─────────────┐
│  🥇 GOLD    │  Build analytics-ready star schema
└─────────────┘
```

### 🥉 Bronze Layer
Loads raw CSV files directly into PostgreSQL without any transformation. Preserves the original data as the source of truth.

### 🥈 Silver Layer
Applies data quality rules:
- Remove duplicate records
- Handle missing / null values
- Standardize text and categorical fields
- Validate numeric ranges

### 🥇 Gold Layer
Builds a **Star Schema** optimized for analytics:

| Table | Type |
|---|---|
| `fact_watch_history` | Fact Table |
| `dim_users` | Dimension |
| `dim_movies` | Dimension |
| `dim_device` | Dimension |
| `dim_date` | Dimension |

---

## 🔁 Airflow DAG

**DAG Name:** `netflix_batch_etl_pipeline`

**Pipeline Flow:**

```
bronze_task  ──►  silver_task  ──►  gold_task
```

| Task | Description |
|---|---|
| `bronze_task` | Ingest raw CSV into Bronze schema |
| `silver_task` | Clean and transform into Silver schema |
| `gold_task` | Build star schema in Gold layer |

---

## ▶️ Running the Pipeline

Trigger the DAG via the **Airflow UI**, or test individual tasks from the CLI:

```bash
# Bronze task
airflow tasks test netflix_batch_etl_pipeline bronze_task 2026-04-01

# Silver task
airflow tasks test netflix_batch_etl_pipeline silver_task 2026-04-01

# Gold task
airflow tasks test netflix_batch_etl_pipeline gold_task 2026-04-01
```

---

## 🌐 Access Services

| Service | URL | Notes |
|---|---|---|
| Airflow UI | http://localhost:8081 | Pipeline monitoring |
| Metabase | http://localhost:3000 | Dashboards & analytics |
| PostgreSQL | `localhost:5433` | Direct DB access |

---

## 📊 Data Visualization

**Metabase** connects to the **Gold layer** in PostgreSQL to serve analytics dashboards.

Example dashboards included:

- 🎞️ Top 10 Most Watched Genres
- 🎬 Top 10 Most Watched Movies
- 📱 User Access by Device Category
- 👥 Users by Age Group
- 📅 Weekend vs Weekday Viewing

---

## 📝 Notes

- This project uses **batch processing**, not streaming.
- The dataset is **synthetic** and intended for analytics and data engineering practice.
- PostgreSQL schemas follow the medallion structure:

```
postgresql://
├── bronze    ← raw ingestion
├── silver    ← cleaned & validated
└── gold      ← analytics-ready (star schema)
```

---

## 👤 Author

**Naufal Adi P.S**

---

> 💡 *Built for learning and portfolio purposes. Feel free to fork and adapt for your own data engineering projects.*
