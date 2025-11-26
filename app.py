import duckdb
import pandas as pd
import streamlit as st
from pathlib import Path

# --- Config ---
DB_PATH = Path(__file__).resolve().parent / "discogs.duckdb"

st.set_page_config(
    page_title="Discogs Warehouse – Latest Snapshot",
    layout="wide",
)

st.title("Discogs Warehouse")
st.caption("Latest snapshot from `model.f_release_latest`")

# --- Data helpers ---
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("SELECT * FROM model.f_release_latest").df()
    con.close()
    return df

df = load_data()

if df.empty:
    st.warning("No data found in `model.f_release_latest`. Run the pipeline first.")
    st.stop()

# --- Sidebar filters ---
st.sidebar.header("Filters")

# Cohort filter
cohorts = sorted([c for c in df["cohort"].dropna().unique()])
selected_cohorts = st.sidebar.multiselect(
    "Cohort",
    options=cohorts,
    default=cohorts,
)

filtered = df.copy()
if selected_cohorts:
    filtered = filtered[filtered["cohort"].isin(selected_cohorts)]

# Price filter (if column exists)
if "lowest_price" in filtered.columns:
    prices = filtered["lowest_price"].dropna()
    if not prices.empty:
        min_price = float(prices.min())
        max_price = float(prices.max())
        price_range = st.sidebar.slider(
            "Lowest price range",
            min_value=0.0,
            max_value=max_price,
            value=(min_price, max_price),
            step=0.5,
        )
        filtered = filtered[
            (filtered["lowest_price"].fillna(0) >= price_range[0])
            & (filtered["lowest_price"].fillna(0) <= price_range[1])
        ]

# --- Summary KPIs ---
cols = st.columns(3)
with cols[0]:
    st.metric("Releases", len(filtered))
with cols[1]:
    if "lowest_price" in filtered.columns and not filtered["lowest_price"].dropna().empty:
        st.metric("Median lowest price", f"{filtered['lowest_price'].median():.2f} €")
with cols[2]:
    if "num_for_sale" in filtered.columns and not filtered["num_for_sale"].dropna().empty:
        st.metric("Total for sale", int(filtered["num_for_sale"].sum()))

st.divider()

# --- Table view ---
st.subheader("Latest snapshot table")

# Optional default sorting: cheapest first if column exists
if "lowest_price" in filtered.columns:
    filtered = filtered.sort_values(["lowest_price", "num_for_sale"], ascending=[True, False])

st.dataframe(
    filtered,
    use_container_width=True,
)

st.caption(
    "Data source: DuckDB `discogs.duckdb` → `model.f_release_latest`. "
    "Filters are applied in-memory on the query result."
)
