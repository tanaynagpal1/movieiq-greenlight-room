import streamlit as st
import pandas as pd
import numpy as np
from src.theme import inject_css
from src.loader import (
    load_raw, load_clean,
    load_raw_from_bytes, load_clean_from_bytes,
    BUDGET_BANDS,
)
from sections import (
    s0_pitch, s1_cutting_room, s2_statistical_tests,
    s3_risk_simulator, s4_conclusions, s5_upload, s6_report, s7_ask_ai,
    coming_soon,
)

st.set_page_config(
    page_title="Movie Revenue Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# ---------------- Pick the active data source ----------------
# If the user has uploaded a CSV via the Upload Data section, use it.
# Otherwise fall back to the bundled movies.csv, so the app is never empty.
if "file_bytes" in st.session_state:
    file_bytes = st.session_state["file_bytes"]
    raw_df = load_raw_from_bytes(file_bytes)
    df = load_clean_from_bytes(file_bytes)
    source_label = st.session_state.get("file_name", "uploaded file")
    source_key = f"upload::{source_label}"
else:
    raw_df = load_raw()
    df = load_clean()
    source_label = "movies.csv (bundled)"
    source_key = "default"

SECTIONS = [
    "📊 Dashboard",
    "Upload Data",
    "Data Quality",
    "Statistical Tests",
    "Risk Simulator",
    "Report",
    "Conclusions",
    "Ask AI",
]

with st.sidebar:
    st.markdown(
        '<div style="font-family:\'Rajdhani\',sans-serif;font-weight:700;'
        'font-size:1.1rem;letter-spacing:.05em;color:#fff;margin-bottom:1.2rem">'
        '◈ MOVIEIQ</div>',
        unsafe_allow_html=True,
    )
    choice = st.radio("Navigation", SECTIONS, label_visibility="collapsed")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;'
        'color:#5C5473;font-weight:600;margin-bottom:.6rem">Filters</div>',
        unsafe_allow_html=True,
    )

    # Widget keys include source_key so switching datasets resets the filters
    # cleanly instead of carrying over stale selections that no longer exist.
    genre_options = sorted(df["genre"].unique())
    selected_genres = st.multiselect(
        "Genre", genre_options, default=genre_options,
        key=f"genre_filter::{source_key}",
    )

    # Only offer bands that actually occur, in the defined order rather than
    # alphabetically — "Blockbuster" should not sort above "Micro/Indie".
    band_options = [b for b in BUDGET_BANDS if b in set(df["budget_band"])]
    selected_bands = st.multiselect(
        "Budget category", band_options, default=band_options,
        key=f"band_filter::{source_key}",
    )

    outcome = st.radio(
        "Box office outcome",
        ["All films", "Profitable only", "Loss only"],
        key=f"outcome_filter::{source_key}",
    )

    vote_min, vote_max = float(df["vote_average"].min()), float(df["vote_average"].max())
    min_vote = st.slider(
        "Min vote average", vote_min, vote_max, vote_min, step=0.1,
        key=f"vote_filter::{source_key}",
    )

    search = st.text_input(
        "Search film title", placeholder="Type part of a title",
        key=f"search_filter::{source_key}",
    )

    # ---- Build the single filtered view every section works from ----
    mask = (
        df["genre"].isin(selected_genres)
        & df["budget_band"].isin(selected_bands)
        & (df["vote_average"] >= min_vote)
    )
    if outcome == "Profitable only":
        mask &= df["success"] == 1
    elif outcome == "Loss only":
        mask &= df["success"] == 0
    if search.strip():
        mask &= df["title"].astype(str).str.contains(
            search.strip(), case=False, regex=False
        )

    df_view = df[mask] if (selected_genres and selected_bands) else df.iloc[0:0]

    st.markdown(
        f'<div style="font-size:.78rem;color:#9089AB;margin-top:.6rem">'
        f'{len(df_view):,} / {len(df):,} films in view</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;'
        f'color:#5C5473;font-weight:600;margin-bottom:.3rem">Data Source</div>'
        f'<div style="font-size:.76rem;color:#9089AB">{source_label}</div>',
        unsafe_allow_html=True,
    )

# ---------------- Routing ----------------
if choice == "Upload Data":
    s5_upload.render(df)
elif df_view.empty:
    st.warning(
        "No films match the current filters. Widen the genre or budget selection, "
        "lower the minimum vote average, clear the title search, or set the outcome "
        "back to all films."
    )
elif choice == "📊 Dashboard":
    s0_pitch.render(df_view)
elif choice == "Data Quality":
    s1_cutting_room.render(raw_df)
elif choice == "Statistical Tests":
    s2_statistical_tests.render(df_view)
elif choice == "Risk Simulator":
    s3_risk_simulator.render(df_view)
elif choice == "Report":
    s6_report.render(df_view, raw_df)
elif choice == "Conclusions":
    s4_conclusions.render(df_view)
elif choice == "Ask AI":
    s7_ask_ai.render(df_view, raw_df)
else:
    coming_soon.render(choice)