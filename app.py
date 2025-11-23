import streamlit as st

st.set_page_config(page_title="Discogs Insights", layout="wide")

st.title("🎛️ Discogs Insights")
st.subheader("A data-driven view into your vinyl & music collecting")

st.write("""
Welcome to **Discogs Insights** — a personal analytics tool for exploring your record 
collection, wantlist, and the vinyl market.  
This app connects to your Discogs data and turns it into insights you can act on as a collector, DJ, or music enthusiast.

### What you can do here
- 🔍 Look up releases and view metadata and artwork  
- 📀 Explore your collection and wantlist visually  
- 📊 See genre breakdowns and collecting trends  
- 💸 Track pricing and market signals *(coming soon)*  
- 🎧 Discover music based on your taste *(coming soon)*  

Use the menu on the left to navigate.
""")

st.info("Tip: Start in **Collector Insights** and enter your Discogs username to begin.")
