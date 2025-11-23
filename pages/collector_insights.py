import streamlit as st

st.title("📀 Collector Insights")
st.write("This is where we will put wantlist + release lookup.")

import streamlit as st
import pandas as pd
from collections import Counter
from discogs_api import get_release  # keep
# from discogs_api import wantlist_items  # not needed for this version

@st.cache_data(ttl=3600)
def cached_release(release_id: str):
    from discogs_api import get_release
    return get_release(release_id)

@st.cache_data(ttl=900)
def cached_wantlist_all(username: str, max_pages: int = 5):
    # fetch first page to learn total pages
    from discogs_api import get_user_wantlist_page
    first = get_user_wantlist_page(username, page=1, per_page=100)
    wants = list(first.get("wants", []))
    total_pages = min(first.get("pagination", {}).get("pages", 1), max_pages)
    for p in range(2, total_pages + 1):
        page = get_user_wantlist_page(username, page=p, per_page=100)
        wants.extend(page.get("wants", []))
    return wants, first.get("pagination", {})

st.set_page_config(page_title="Discogs Insights")
st.title("🎛️ Discogs Insights")

# ---------- Release lookup ----------
release_id = st.text_input("Enter Discogs Release ID", "249504")  # example: Daft Punk - Homework
if st.button("Fetch Release Info"):
    data = cached_release(release_id)
    if "title" in data:
        st.subheader(data["title"])
        artist = ", ".join(a["name"] for a in data.get("artists", []))
        colA, colB = st.columns([1, 2])
        with colA:
            from discogs_api import primary_image
            img = primary_image(data)
            if img:
                st.image(img, use_container_width=True)
        with colB:
            st.markdown(f"**Artist:** {artist}")
            st.markdown(f"**Year:** {data.get('year', '—')}")
            st.markdown(f"**Genres:** {', '.join(data.get('genres', [])) or '—'}")
            st.markdown(f"**Styles:** {', '.join(data.get('styles', [])) or '—'}")
    else:
        st.error("Release not found or API limit reached.")

# ---------- Wantlist + thumbnails + genres ----------
st.subheader("🔎 View your Wantlist")
username = st.text_input("Enter your Discogs username", key="wantlist_username")

if st.button("Fetch Wantlist & Genres", key="wantlist_btn"):
    if not username.strip():
        st.error("Please enter a username.")
    else:
        wants, meta = cached_wantlist_all(username)
        if not wants:
            st.error("Could not fetch wantlist. Check username or token.")
        else:
            st.write(f"Total wants (Discogs): {meta.get('items','?')} • Items fetched: {len(wants)}")

            # --- Thumbnail preview (first 10) ---
            st.subheader("🎨 Preview")
            for item in wants[:10]:
                info = item["basic_information"]
                col1, col2 = st.columns([1, 4])
                with col1:
                    img = info.get("cover_image")
                    if img:
                        st.image(img, width=80)
                with col2:
                    artist = ", ".join(a["name"] for a in info.get("artists", []))
                    st.markdown(f"**{info.get('title','')}**")
                    st.write(artist)
                    st.write(info.get("year", "—"))

            # --- Genre aggregation chart ---
            counter = Counter()
            for item in wants:
                info = item["basic_information"]
                for g in info.get("genres", []):
                    counter[g] += 1

            if counter:
                df = pd.DataFrame(counter.items(), columns=["genre", "count"]).sort_values("count", ascending=False).head(15)
                st.subheader("Top Genres in Your Wantlist")
                st.bar_chart(df.set_index("genre"))  # no custom colors
            else:
                st.info("No genres found in wantlist items.")