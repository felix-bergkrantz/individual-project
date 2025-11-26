# Discogs Warehouse

A local DuckDB + Discogs API pipeline for discovering releases, taking market snapshots, and building lightweight analytics tables.

---

## What this repo does

1. Discovers releases for defined cohorts and stores their IDs in `model.d_release`.
2. Backfills metadata (title, artist, year, label) for those releases.
3. Takes market snapshots (`lowest_price`, `num_for_sale`) from the Discogs API and stores them as raw JSON.
4. Builds analytical tables (`prep.lowest`, `model.f_release_latest`) for exploring the latest market state.
5. Runs all SQL models in order with `run_sql.py`.
6. Displays results in terminal using `show_top.py`.

Database file: `discogs.duckdb` in the repository root.

---

## Data model

**Schemas**
- `raw`
- `prep`
- `model`

**Tables**
- `model.d_release` – release IDs + metadata + cohort.
- `raw.raw_release_snapshots` – raw JSON snapshots from the API.
- `prep.lowest` – flattened numeric fields + timestamp.
- `model.f_release_latest` – the latest snapshot per release with joined metadata.

---

## Python scripts

### Core pipeline
- **env.py** – loads Discogs token from `.env`.
- **check_api.py** – simple connectivity test to verify the token.
- **cohorts.py** – defines search cohorts.
- **discovery.py**
  - `discover_ids()` inserts release IDs for each cohort.
  - `backfill_meta()` fills in metadata for missing releases.
- **snapshot_lowest.py** – takes snapshots of lowest prices and number of items for sale.

### SQL runner
- **run_sql.py** – executes all SQL files (`00_raw.sql`, `01_prep.sql`, `02_model.sql`) against the DuckDB database.

### Output
- **show_top.py** – prints the full `model.f_release_latest` table in a readable fixed-width format.

---

## SQL files

- **00_raw.sql** – creates schemas and `model.d_release`.
- **01_prep.sql** – transforms raw snapshots into a typed table.
- **02_model.sql** – builds the “latest snapshot per release” fact table.

---

## Setup

### 1. Environment
Create a `.env` file in the repo root:

```bash
DISCOGS_TOKEN=your_discogs_api_token
