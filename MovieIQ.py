from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="MovieIQ — The Greenlight Room",
                   page_icon="🎬", layout="wide")

DATA = Path(__file__).parent / "data" / "movies.csv"

@st.cache_data
def load():
    return pd.read_csv(DATA)

df = load()

st.title("MovieIQ — The Greenlight Room")
st.caption("A risk-intelligence console for film investment.")
st.metric("Rows loaded", f"{len(df):,}")