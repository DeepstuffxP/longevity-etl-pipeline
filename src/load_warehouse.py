from load_raw import get_conn


def get_latest_snapshot(cur):
    cur.execute(
        "SELECT pulled_at::date, payload FROM raw.athletes_snapshot "
        "ORDER BY pulled_at DESC LIMIT 1"
    )
    snapshot_date, athletes = cur.fetchone()
    return snapshot_date, athletes


def load_athletes(cur, athletes):
    for a in athletes:
        slug = a["AthleteSlug"]
        name = a.get("Name")
        division = a.get("Division")
        flag = a.get("Flag")

        
        dob = a.get("DateOfBirth")
        birth_year = dob["Year"] if dob else None

        cur.execute(
            """
            INSERT INTO warehouse.dim_athlete
                (athlete_slug, name, division, flag_raw, birth_year)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (athlete_slug) DO UPDATE SET
                name = EXCLUDED.name,
                division = EXCLUDED.division,
                flag_raw = EXCLUDED.flag_raw,
                birth_year = EXCLUDED.birth_year
            """,
            (slug, name, division, flag, birth_year),
        )
    print(f"athletes loaded: {len(athletes)}")


def get_athlete_keys(cur):
    cur.execute("SELECT athlete_slug, athlete_key FROM warehouse.dim_athlete")
    keys = {}
    for slug, key in cur.fetchall():
        keys[slug] = key
    return keys


def load_lab_results(cur, athletes, keys):
    count = 0
    for a in athletes:
        athlete_key = keys[a["AthleteSlug"]]

        for lab_record in a.get("Biomarkers", []):
            test_date = lab_record["Date"]

            for marker_code, value in lab_record.items():
                if marker_code == "Date":
                    continue          
                if value is None:
                    continue          

                cur.execute(
                    """
                    INSERT INTO warehouse.fact_biomarker_result
                        (athlete_key, test_date, marker_code, value)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (athlete_key, test_date, marker_code)
                    DO UPDATE SET value = EXCLUDED.value
                    """,
                    (athlete_key, test_date, marker_code, round(value, 4)),
                )
                count += 1
    print(f"lab values loaded: {count}")


def load_daily_snapshot(cur, athletes, keys, snapshot_date):
    for a in athletes:
        athlete_key = keys[a["AthleteSlug"]]
        crowd_count = a.get("CrowdCount")

        
        if crowd_count:
            crowd_age = a.get("CrowdAge")
        else:
            crowd_age = None

        cur.execute(
            """
            INSERT INTO warehouse.fact_athlete_daily
                (snapshot_date, athlete_key, current_placement,
                 crowd_age, crowd_count, submission_count)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (snapshot_date, athlete_key) DO UPDATE SET
                current_placement = EXCLUDED.current_placement,
                crowd_age = EXCLUDED.crowd_age,
                crowd_count = EXCLUDED.crowd_count,
                submission_count = EXCLUDED.submission_count
            """,
            (
                snapshot_date,
                athlete_key,
                a.get("CurrentPlacement"),
                crowd_age,
                crowd_count,
                a.get("SubmissionCount"),
            ),
        )
    print(f"daily rows loaded: {len(athletes)}")


def main():
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            snapshot_date, athletes = get_latest_snapshot(cur)
            print(f"using snapshot from {snapshot_date} with {len(athletes)} athletes")

            load_athletes(cur, athletes)
            keys = get_athlete_keys(cur)
            load_lab_results(cur, athletes, keys)
            load_daily_snapshot(cur, athletes, keys, snapshot_date)
    conn.close()
    print("done")


if __name__ == "__main__":
    main()