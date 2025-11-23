from pathlib import Path
import duckdb

# Connect to the root DB
DB = Path(__file__).resolve().parents[2] / "discogs.duckdb"
con = duckdb.connect(str(DB))

# Grab all columns from the fact table
query = """
    select
        release_id,
        title,
        artist,
        year,
        label,
        cohort,
        lowest_price,
        num_for_sale,
        ingested_at
    from model.f_release_latest
    order by cohort, artist, title
"""

rows = con.execute(query).fetchall()

# Simple header
print(
    f"{'release_id':10} | {'title':35} | {'artist':25} | {'year':4} | "
    f"{'label':25} | {'cohort':10} | {'price':8} | {'for_sale':8} | {'ingested_at'}"
)
print("-" * 140)

for (
    release_id,
    title,
    artist,
    year,
    label,
    cohort,
    lowest_price,
    num_for_sale,
    ingested_at,
) in rows:
    print(
        f"{release_id:10} | "
        f"{(title or '')[:35]:35} | "
        f"{(artist or '')[:25]:25} | "
        f"{str(year or ''):4} | "
        f"{(label or '')[:25]:25} | "
        f"{(cohort or '')[:10]:10} | "
        f"{(lowest_price if lowest_price is not None else 0):8.2f} | "
        f"{(num_for_sale or 0):8d} | "
        f"{ingested_at}"
    )
