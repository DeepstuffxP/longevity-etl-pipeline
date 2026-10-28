import json
import time
from datetime import datetime, timezone
from pathlib import Path
import requests

BASE_URL = "https://longevityworldcup.com/api/data"
ENDPOINTS = ["athletes", "divisions", "flags"]
RAW_DIR = Path("data/raw")

def fetch(endpoint: str):
    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers = {"User-Agent": "longevity-etl-portfolio/0.1"},
        timeout = 30,
    )
    response.raise_for_status()
    return response.json()

def save_raw (data, endpoint: str, stamp: str) -> Path:
    folder = RAW_DIR / endpoint
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{endpoint}_{stamp}.json"
    path.write_text(json.dumps(data, indent=2), encoding = "utf-8")
    return path


if __name__ == "__main__":
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    for endpoint in ENDPOINTS:
        data = fetch(endpoint)
        path = save_raw(data, endpoint, stamp)
        print(f"{endpoint}: {len(data)} records -> {path}")
        time.sleep(1)
