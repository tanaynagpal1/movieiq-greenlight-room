import streamlit as st
import pandas as pd
from src.theme import inject_css
from src.loader import load_clean
from sections import s0_pitch, s1_cutting_room, coming_soon

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

if choice == "📊 Dashboard":
    s0_pitch.render(df)
elif choice == "Data Quality":
    s1_cutting_room.render()
else:
    coming_soon.render(choice)