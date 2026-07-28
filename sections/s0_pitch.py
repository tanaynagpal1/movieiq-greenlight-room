"""Dashboard — KPIs + charts + (soon) the predictor."""
import streamlit as st
from src.theme import kpi_card
from src.charts import breakeven_scatter, genre_success_bar, correlation_heatmap


def render(df):
    st.markdown('<div class="hero-kicker">Build v0.4 · Dashboard online</div>',
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

    st.markdown('<div class="section-title">Exploratory Analysis</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Where the money actually goes.</div>',
                unsafe_allow_html=True)

    left, right = st.columns([1.5, 1])
    with left:
        st.markdown(
            '<div class="panel"><div class="panel-title">Budget vs Revenue</div>',
            unsafe_allow_html=True)
        st.plotly_chart(breakeven_scatter(df), use_container_width=True,
                         config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown(
            '<div class="panel"><div class="panel-title">Correlation Matrix</div>',
            unsafe_allow_html=True)
        st.plotly_chart(correlation_heatmap(df), use_container_width=True,
                         config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="panel"><div class="panel-title">Success Rate by Genre</div>',
        unsafe_allow_html=True)
    st.plotly_chart(genre_success_bar(df), use_container_width=True,
                     config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)