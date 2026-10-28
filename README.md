# Longevity ETL Pipeline

A daily data pipeline built in Python. It pulls the public Longevity World Cup leaderboard (a competition ranked by biological age), saves an untouched copy of everything it receives, and loads a cleaned version into a PostgreSQL warehouse. Apache Airflow, running in Docker, runs it every day and retries it when something fails.

The API only shows today's leaderboard. Because the pipeline stores a snapshot every day, it slowly builds a history of who moved up and down the rankings, which the source doesn't give you.

I built it to learn the data engineering side of things: orchestration, warehouse tables, and loads that are safe to re-run.

## Architecture

```
Longevity World Cup API
        ↓
   extract.py          → data/raw/*.json (dated, untouched copies)
        ↓
   load_raw.py         → raw.athletes_snapshot (whole JSON, as JSONB)
        ↓
   load_warehouse.py   → dim_athlete
                       → fact_biomarker_result
                       → fact_athlete_daily

Airflow runs these three steps daily, in order, with retries
```

## When the pipeline runs

1. Airflow starts the DAG on its daily schedule, or when you press Trigger.
2. `extract.py` calls the API and saves each response as a JSON file named with the pull time. Nothing is cleaned at this point. It's the original receipt.
3. `load_raw.py` copies the athletes file into Postgres as one JSONB row. The filename is unique, so loading the same file twice does nothing.
4. `load_warehouse.py` reads the newest raw snapshot and writes one row per athlete into `dim_athlete`. Only the birth year is kept.
5. It reshapes each athlete's nested lab records into one row per athlete, date, and marker in `fact_biomarker_result`.
6. It writes one row per athlete per day into `fact_athlete_daily`: placement, crowd age, crowd count, and submission count.
7. Every insert is an upsert (`ON CONFLICT ... DO UPDATE`), so running the pipeline twice updates rows instead of duplicating them.
8. If a task fails, Airflow retries it twice before marking it red and stopping the chain.

At the time of writing the warehouse holds 244 athletes and 3,966 lab values.

## Stack

- Python, requests, psycopg2
- PostgreSQL, with JSONB for the raw layer
- Apache Airflow 2.10 in Docker

## Run it

I built and tested this on Windows with Docker Desktop and a local PostgreSQL install. Postgres runs on your machine, and only Airflow runs in Docker.

Set up Python:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create an empty Postgres database called `longevity`, then build the tables:

```bash
psql -U postgres -d longevity -f sql/01_schema.sql
psql -U postgres -d longevity -f sql/02_warehouse.sql
```

Copy `.env.example` to `.env` and put in your Postgres password. Then try the steps by hand:

```bash
python src/extract.py
python src/load_raw.py
python src/load_warehouse.py
```

A successful warehouse load prints something like this:

```
using snapshot from 2026-10-25 with 244 athletes
athletes loaded: 244
lab values loaded: 3966
daily rows loaded: 244
done
```

Run it a second time. The counts in the database shouldn't change, because the loads are safe to repeat.

To run it with Airflow instead:

```bash
docker compose up
```

Wait a few minutes, then open `http://localhost:8080` and log in as `admin`. Get the generated password with:

```bash
docker compose exec airflow cat /opt/airflow/standalone_admin_password.txt
```

Switch on the `longevity_pipeline` DAG and press Trigger. Airflow only runs while Docker is running, so a closed laptop means a skipped day.

## Things I did on purpose

- **Keep the raw data.** If my cleaning logic turns out to be wrong, I fix it and reprocess instead of asking the API again.
- **Privacy.** The API response includes contact emails and full birth dates for real people. The warehouse keeps neither. The raw JSON files on disk do contain them, so the `data/` folder is gitignored and never committed.
- **Facts that change vs. facts that don't.** A lab result never changes once recorded, so it's upserted. Placement and crowd guesses change daily, so they get a snapshot row per day.
- **Zero isn't always zero.** A crowd age of 0 with no guesses means nobody guessed yet, so it's stored as NULL.

## Known limitations

- There are no automated data quality checks yet. That's the next thing I plan to add.
- `marker_code` is stored as plain text in the fact table. It isn't enforced as a foreign key to `dim_marker`, and I haven't verified that every marker in the data exists in that lookup table.
- Country names are stored as they arrive, so "USA" and "United States" are separate values, and some "flags" aren't countries at all.
- Placement history, badges, and proof image links are saved in the raw layer but not modeled in the warehouse yet.
- It's small: 244 athletes, one machine, one Airflow container. The point of the project is the engineering, not the volume.

## To do

- [ ] add data quality checks as an Airflow task
- [ ] clean country names
- [ ] add a foreign key from `fact_biomarker_result` to `dim_marker`
- [ ] model badges and placements
- [ ] add a dashboard

## Data source

Public API from [Longevity World Cup](https://longevityworldcup.com). It describes real people, so please use it respectfully. This project is for learning data engineering, not for republishing anyone's personal health information.
