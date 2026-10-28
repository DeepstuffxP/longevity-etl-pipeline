import json
import os
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv

load_dotenv()

RAW_DIR = Path("data/raw/athletes")


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def pulled_at_from_filename(path: Path) -> datetime:
    
    stamp = path.stem.split("_")[-1]
    return datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)


INSERT_SQL = """
    INSERT INTO raw.athletes_snapshot (pulled_at, source_file, payload)
    VALUES (%s, %s, %s)
    ON CONFLICT (source_file) DO NOTHING
"""

if __name__ == "__main__":
    files = sorted(RAW_DIR.glob("athletes_*.json"))
    if not files:
        raise SystemExit(f"No files found in {RAW_DIR}")

    loaded = skipped = 0
    conn = get_conn()
    try:
        with conn:  # commits if everything works, rolls back if anything fails
            with conn.cursor() as cur:
                for path in files:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    cur.execute(
                        INSERT_SQL,
                        (pulled_at_from_filename(path), path.name, Json(data)),
                    )
                    if cur.rowcount == 1:
                        loaded += 1
                        print(f"loaded : {path.name} ({len(data)} athletes)")
                    else:
                        skipped += 1
                        print(f"skipped: {path.name} (already loaded)")
    finally:
        conn.close()

    print(f"Done. loaded={loaded}, skipped={skipped}")