import streamlit as st
import pandas as pd
import numpy as np
from src.theme import inject_css
from src.loader import load_clean
from sections import s0_pitch, s1_cutting_room, s2_statistical_tests, s3_risk_simulator, s4_conclusions, coming_soon

st.set_page_config(
    page_title="Movie Revenue Analysis",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

df = load_clean()

SECTIONS = [
    "📊 Dashboard",
    "Data Quality",
    "Statistical Tests",
    "Risk Simulator",
    "Conclusions",
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

    genre_options = sorted(df["genre"].unique())
    selected_genres = st.multiselect("Genre", genre_options, default=genre_options)

    vote_min, vote_max = float(df["vote_average"].min()), float(df["vote_average"].max())
    min_vote = st.slider("Min vote average", vote_min, vote_max, vote_min, step=0.1)

    if selected_genres:
        df_view = df[df["genre"].isin(selected_genres) & (df["vote_average"] >= min_vote)]
    else:
        df_view = df.iloc[0:0]  # empty selection -> empty view, no crash

    st.markdown(
        f'<div style="font-size:.78rem;color:#9089AB;margin-top:.6rem">'
        f'{len(df_view):,} / {len(df):,} films in view</div>',
        unsafe_allow_html=True,
    )

if df_view.empty:
    st.warning("No films match the current filters. Adjust genre or minimum vote average in the sidebar.")
elif choice == "📊 Dashboard":
    s0_pitch.render(df_view)
elif choice == "Data Quality":
    s1_cutting_room.render()
elif choice == "Statistical Tests":
    s2_statistical_tests.render(df_view)
elif choice == "Risk Simulator":
    s3_risk_simulator.render(df_view)
elif choice == "Conclusions":
    s4_conclusions.render(df_view)
else:
    coming_soon.render(choice)