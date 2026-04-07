-- Bronze schema for raw ingested data
CREATE SCHEMA IF NOT EXISTS bronze;

-- Silver schema for cleaned and standardized data
CREATE SCHEMA IF NOT EXISTS silver;

-- Gold schema for dimensional model and analytics-ready tables
CREATE SCHEMA IF NOT EXISTS gold;