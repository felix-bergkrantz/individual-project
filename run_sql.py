from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parent
DB = ROOT / "discogs.duckdb"
SQL_DIR = ROOT / "discogs_warehouse" / "sql"

FILES = [
    "00_raw.sql",
    "01_prep.sql",
    "02_model.sql",
]

con = duckdb.connect(str(DB))

for fname in FILES:
    sql_path = SQL_DIR / fname
    print(f"Running {sql_path} ...")
    con.execute(sql_path.read_text())

print("Done.")
