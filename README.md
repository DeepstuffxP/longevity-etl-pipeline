# US-India Trade Pipeline

A data engineering project that pulls monthly US-India trade data (what the US imports from and exports to India, by commodity) from the US Census Bureau International Trade API, stores the raw JSON in S3, loads it into PostgreSQL, transforms it with plain SQL into a star schema, checks data quality with SQLAlchemy, and shows the results in a Power BI dashboard. It is a small-data project built to practice cloud storage, warehouse modelling and handling revised data. It is not a big data project.

## Status

Work in progress. Honest checklist:

- Done: AWS account, S3 bucket in Mumbai (ap-south-1), limited IAM user with access to one bucket only, Census API key, API exploration scripts
- Not done yet: extract script, S3 upload, Postgres load, SQL transforms, star schema, SQLAlchemy models and checks, dashboard

This README is updated as each part is finished. Real numbers (rows loaded, date range, object counts) are logged in `metrics.md` only after they are measured.

## Architecture

```
Census Trade API (exports + imports, India only)
  -> Python extract (requests)
  -> S3 raw/ (JSON, partitioned by year/month)
  -> Postgres raw schema (JSONB)
  -> SQL transforms
  -> star schema: dim_country, dim_commodity, dim_date, fact_trade
  -> SQLAlchemy Core: table models, data quality checks, analytics queries, run audit table
  -> Power BI Desktop dashboard (one page)
```

Planned later, only if it stays honest: a PySpark stage that converts raw JSON to Parquet in S3. At this data size Spark is not needed, so if it is added, it is added to learn the tool and the README will say so.

## When the pipeline runs (planned)

1. The extract script reads the API key and bucket name from `.env`.
2. It requests India's monthly export and import rows from the Census API.
3. It uploads the raw JSON to S3 under `raw/`, one path per year and month.
4. The load script reads the raw files and writes them into the Postgres raw schema.
5. SQL scripts build the dimension tables and `fact_trade` from the raw layer.
6. Data quality checks run after the load, and the results are written to an audit table.
7. Re-running the pipeline updates existing rows instead of duplicating them.

## Data source

- US Census Bureau International Trade API, HS-level monthly data, endpoints `exports/hs` and `imports/hs`
- India is country code `5330`, confirmed from a test call to the API
- Exports use `E_COMMODITY` and `ALL_VAL_MO`. Imports use `I_COMMODITY` and `GEN_VAL_MO`
- Census revises previously released data each year when April statistics are published, so the load is designed to upsert and to be re-runnable

## Security

- The API key and bucket name live in `.env`, which is ignored by Git. `.env.example` shows the variable names
- The pipeline uses an IAM user that can list one bucket and read and write the `raw/` prefix only, not root credentials

## Setup

1. Clone the repo and create a virtual environment: `python3 -m venv .venv`, then `source .venv/bin/activate`
2. Install packages: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your own values
4. Request a free Census API key at https://api.census.gov/data/key_signup.html
5. Configure AWS CLI credentials for a user limited to your own bucket

## Skills demonstrated

Shown so far:

- Cloud setup on AWS: S3 bucket in ap-south-1 and a least-privilege IAM user limited to one bucket, tested by confirming that access to the bucket works and that listing all buckets is denied
- API exploration before coding: read the variable lists from the Census API, verified India's country code and the import column names with test calls
- Secrets handling: API key and bucket name kept in `.env`, ignored by Git, with a safe `.env.example`
- Linux development environment: WSL2 Ubuntu, Python virtual environment, pinned `requirements.txt`

Planned, added to the list above only when they work:

- Extract and load: Python with requests and boto3, raw JSON stored in S3 by year and month, loaded into a Postgres raw schema
- Warehouse modelling: plain SQL transforms into a star schema with dimension and fact tables
- Re-runnable loads: upserts so repeat runs and Census data revisions do not create duplicates
- Data quality: SQLAlchemy Core checks after each load, with results saved to an audit table
- Analytics: SQL queries over the fact table and a one-page Power BI dashboard

## Tech

Python, requests, boto3, AWS S3, PostgreSQL, SQL, SQLAlchemy Core, Power BI Desktop, WSL2 Ubuntu
