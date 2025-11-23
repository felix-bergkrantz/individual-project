from pathlib import Path
import time
import duckdb
from discogs_client import Client
from discogs_client.exceptions import HTTPError
from env import DISCOGS_TOKEN
from cohorts import COHORTS

# Connect to DB
DB = Path(__file__).resolve().parents[1] / "discogs.duckdb"
con = duckdb.connect(str(DB))

# Discogs client
d = Client("discogs-warehouse/1.0", user_token=DISCOGS_TOKEN)


def discover_ids(name, cfg, pages: int = 1, per_page: int = 100):
    """Find release_ids for a cohort and insert them into model.d_release with empty meta."""
    ids = set()

    for page in range(1, pages + 1):
        wait = 1.5
        while True:
            try:
                res = d.search(
                    type="release",
                    format=cfg["format"],
                    style=cfg["style"],
                    year=cfg["year"],
                    per_page=per_page,
                    page=page,
                )
                items = list(res.page(page))  # fetch ONLY this page
                break
            except HTTPError as e:
                if getattr(e, "status_code", None) == 429:
                    time.sleep(wait)
                    wait = min(wait * 1.6, 12)
                    continue
                raise

        for r in items:
            ids.add(r.id)

        time.sleep(1.2)  # gentle pacing

    # NOTE: model.d_release (schema + table)
    con.executemany(
        """
        insert or ignore into model.d_release
            (release_id, title, artist, year, label, cohort)
        values (?, NULL, NULL, NULL, NULL, ?)
        """,
        [(rid, name) for rid in ids],
    )

    print(f"{name}: inserted/kept {len(ids)} ids")


def fetch_meta(rid, retries: int = 5):
    """Fetch title/artist/year/label for a single release_id, with retries."""
    wait = 1.0
    for _ in range(retries):
        try:
            rel = d.release(rid)
            title = rel.title
            # take first artist name if present
            artist = rel.artists[0].name if getattr(rel, "artists", None) else None
            year = rel.year or None
            label = rel.labels[0].name if getattr(rel, "labels", None) else None
            return title, artist, year, label
        except Exception:
            time.sleep(wait)
            wait = min(wait * 2, 15)
    return None


def backfill_meta(limit: int = 150):
    """Fill in missing metadata in model.d_release."""
    rows = con.execute(
        "select release_id from model.d_release where title is NULL limit ?",
        [limit],
    ).fetchall()

    for (rid,) in rows:
        meta = fetch_meta(rid)
        if meta:
            title, artist, year, label = meta
            con.execute(
                """
                update model.d_release
                set title = ?, artist = ?, year = ?, label = ?
                where release_id = ?
                """,
                [title, artist, year, label, rid],
            )
        time.sleep(0.2)

    print(f"Backfilled {len(rows)} rows")


if __name__ == "__main__":
    # 1) discover ids for each cohort
    for name, cfg in COHORTS.items():
        discover_ids(name, cfg, pages=1)

    # 2) backfill metadata
    backfill_meta(limit=150)
    print("Done.")
