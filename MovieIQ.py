import pandas as pd
import streamlit as st

from src.theme import inject_css, kpi_card

st.set_page_config(
    page_title="MovieIQ — The Greenlight Room",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

from src.loader import load_clean

df = load_clean()

st.markdown('<div class="hero-kicker">Build v0.2 &middot; Design system online</div>',
            unsafe_allow_html=True)
st.markdown('<div class="hero-title">Movies <span>Revenue Analysis</span></div>',
            unsafe_allow_html=True)
st.markdown('<div class="hero-sub">A risk-intelligence console for film investment.</div>',
            unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    kpi_card("Films in catalogue", f"{len(df):,}", "rows loaded from movies.csv", tone="purple", pct=100)
with c2:
    kpi_card("Success base rate", f"{df.success.mean() * 100:.1f}%",
             "revenue > budget", tone="gold", pct=int(df.success.mean()*100))
with c3:
    kpi_card("Median ROI", f"+{df.roi.median() * 100:.1f}%",
             f"x{df.roi.median() + 1:.2f} multiplier", tone="teal", pct=65)
with c4:
    kpi_card("Capital at risk", f"${df.budget.sum() / 1e9:.1f}B",
             "sum of all budgets", tone="red", pct=85)
st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
st.markdown('<div class="hero-title" style="font-size:1.6rem">The Cutting Room</div>',
            unsafe_allow_html=True)

from src.audit import render_audit_panel
render_audit_panel()