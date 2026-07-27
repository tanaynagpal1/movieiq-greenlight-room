import streamlit as st

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
    "00 · Overview",
    "01 · Data Quality",
    "02 · Exploratory Analysis",
    "03 · Statistical Tests",
    "04 · Prediction Model",
    "05 · Risk Simulator",
    "06 · Conclusions",
]

with st.sidebar:
    st.markdown(
        '<div style="font-family:\'Rajdhani\',sans-serif;font-weight:700;'
        'font-size:1.1rem;letter-spacing:.05em;color:#fff;margin-bottom:1.2rem">'
        '◈ MOVIEIQ</div>',
        unsafe_allow_html=True,
    )
    choice = st.radio("Navigation", SECTIONS, label_visibility="collapsed")

if choice == "00 · Overview":
    s0_pitch.render(df)
elif choice == "01 · Data Quality":
    s1_cutting_room.render()
else:
    coming_soon.render(choice.split("· ")[1])