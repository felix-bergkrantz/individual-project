# Discogs Warehouse

Local DuckDB + Discogs API pipeline for discovering releases, taking market snapshots, and building simple analytics tables.

---

## What this repo does

1. **Discover releases** for defined cohorts and store IDs in `model.d_release`.   
2. **Backfill metadata** (title, artist, year, label) into `model.d_release`. :contentReference[oaicite:1]{index=1}  
3. **Snapshot market data** (`lowest_price`, `num_for_sale`) into `raw.raw_release_snapshots`. :contentReference[oaicite:2]{index=2}  
4. **Build analytics tables** (`prep.lowest`, `model.f_release_latest`).   
5. **Run all SQL models at once using `run_sql.py`**. :contentReference[oaicite:4]{index=4}  
6. **Show results in terminal** via `show_top.py`. :contentReference[oaicite:5]{index=5}  

Database: `discogs.duckdb` at repo root.

---

## Data model

- **Schemas**: `raw`, `prep`, `model` (created in `00_raw.sql`). :contentReference[oaicite:6]{index=6}  
- **model.d_release**: release_id + metadata + cohort.  
- **raw.raw_release_snapshots**: raw JSON snapshots.  
- **prep.lowest**: flattened numeric fields + timestamp. :contentReference[oaicite:7]{index=7}  
- **model.f_release_latest**: one latest snapshot per release. :contentReference[oaicite:8]{index=8}  

---

## Python scripts

### Core pipeline  
- **env.py** – loads Discogs token from `.env`. :contentReference[oaicite:9]{index=9}  
- **check_api.py** – quick API connectivity check. :contentReference[oaicite:10]{index=10}  
- **cohorts.py** – defines search cohorts. :contentReference[oaicite:11]{index=11}  
- **discovery.py**  
  - `discover_ids()` inserts releases into `model.d_release`.  
  - `backfill_meta()` fills title/artist/year/label. :contentReference[oaicite:12]{index=12}  
- **snapshot_lowest.py** – retrieves lowest_price + num_for_sale for selected releases. :contentReference[oaicite:13]{index=13}  

### SQL runner  
- **run_sql.py** – executes `00_raw.sql`, `01_prep.sql`, `02_model.sql` in order and updates the DB. :contentReference[oaicite:14]{index=14}  

### Output  
- **show_top.py** – prints the full `model.f_release_latest` table. :contentReference[oaicite:15]{index=15}  

---

## SQL files

- **00_raw.sql** – schemas + `model.d_release`. :contentReference[oaicite:16]{index=16}  
- **01_prep.sql** – transforms raw snapshots → `prep.lowest`. :contentReference[oaicite:17]{index=17}  
- **02_model.sql** – builds latest snapshot fact table. :contentReference[oaicite:18]{index=18}  

---

## Required setup

### Environment
`.env` in repo root:
```bash
DISCOGS_TOKEN=your_discogs_token_here
