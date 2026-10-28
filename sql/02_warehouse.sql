CREATE TABLE IF NOT EXISTS warehouse.dim_athlete (
    athlete_key  SERIAL PRIMARY KEY,
    athlete_slug TEXT UNIQUE NOT NULL,
    name         TEXT,
    division     TEXT,
    flag_raw     TEXT,
    birth_year   INT
);

CREATE TABLE IF NOT EXISTS warehouse.fact_biomarker_result (
    athlete_key INT REFERENCES warehouse.dim_athlete(athlete_key),
    test_date   DATE,
    marker_code TEXT,
    value       NUMERIC,
    PRIMARY KEY (athlete_key, test_date, marker_code)
);

CREATE TABLE IF NOT EXISTS warehouse.fact_athlete_daily (
    snapshot_date     DATE,
    athlete_key       INT REFERENCES warehouse.dim_athlete(athlete_key),
    current_placement INT,
    crowd_age         NUMERIC,
    crowd_count       INT,
    submission_count  INT,
    PRIMARY KEY (snapshot_date, athlete_key)
);