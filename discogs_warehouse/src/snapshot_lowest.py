import os
import time
import json
import requests
import duckdb
from pathlib import Path
from dotenv import load_dotenv

# --- DB connection ---
DB = Path(__file__).resolve().parents[2] / "discogs.duckdb"
con = duckdb.connect(str(DB))

# --- Token / headers ---
env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(env_path)
TOKEN = os.getenv("DISCOGS_TOKEN")
if not TOKEN:
    raise RuntimeError("Missing DISCOGS_TOKEN in .env")

HEAD = {
    "User-Agent": "discogs-warehouse-basic/1.0",
    "Authorization": f"Discogs token={TOKEN}",
}
BASE = "https://api.discogs.com"

# raw table for snapshots
con.execute("create schema if not exists raw")
con.execute("create table if not exists raw.raw_release_snapshots(json json)")

def _get(url):
    """GET with simple retry + rate limit handling."""
    wait = 0.8
    for _ in range(6):
        r = requests.get(url, headers=HEAD, timeout=30)

        # rate limited → wait, then retry
        if r.status_code == 429:
            ra = float(r.headers.get("Retry-After", wait))
            time.sleep(max(wait, ra))
            wait = min(wait * 1.6, 12)
            continue

        # forbidden / not found → treat as "no data"
        if r.status_code in (403, 404):
            return None

        # server error → retry a few times
        if r.status_code >= 500:
            time.sleep(wait)
            continue

        # ok or client error < 400
        r.raise_for_status()
        return r.json()

    return None  # gave up after retries


def snapshot(limit=30):
    """Take a simple snapshot of lowest_price + num_for_sale for some releases."""
    ts = time.time()
    rids = [
        r[0]
        for r in con.execute(
            "select release_id from model.d_release where title is not null limit ?",
            [limit],
        ).fetchall()
    ]

    rows = []

    for rid in rids:
        rel = _get(f"{BASE}/releases/{rid}")
        if not rel:
            print(f"skip {rid} (no release json)")
            continue

        snap = {
            "release_id": rid,
            "lowest_price": rel.get("lowest_price"),
            "num_for_sale": rel.get("num_for_sale"),
            "_ingested_at": ts,
        }

        rows.append(json.dumps(snap))
        time.sleep(0.4)  # be gentle with API

    if rows:
        con.executemany(
            "insert into raw.raw_release_snapshots select json(?)",
            [(r,) for r in rows],
        )
        print(f"inserted {len(rows)} snapshots")
    else:
        print("no snapshots")


if __name__ == "__main__":
    snapshot(limit=30)
