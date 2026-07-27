"""Section 00 — The Pitch."""
import streamlit as st
from src.theme import kpi_card


def render(df):
    st.markdown('<div class="hero-kicker">Build v0.3 · Navigation online</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Movie <span>Revenue Analysis</span></div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">A risk-intelligence console for film investment.</div>',
                unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Films in catalogue", f"{len(df):,}",
                 "rows loaded from movies.csv", tone="purple", pct=100)
    with c2:
        kpi_card("Success base rate", f"{df.success.mean() * 100:.1f}%",
                 "revenue > budget", tone="gold", pct=int(df.success.mean() * 100))
    with c3:
        kpi_card("Median ROI", f"+{df.roi.median() * 100:.1f}%",
                 f"x{df.roi.median() + 1:.2f} multiplier", tone="teal", pct=65)
    with c4:
        kpi_card("Capital at risk", f"${df.budget.sum() / 1e9:.1f}B",
                 "sum of all budgets", tone="red", pct=85)