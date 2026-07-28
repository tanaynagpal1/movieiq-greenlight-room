"""Dashboard — KPIs + charts + prediction model, all on one page."""
import streamlit as st
from src.theme import kpi_card
from src.charts import breakeven_scatter, genre_success_bar, correlation_heatmap
from src.model import train_model, predict_one


def render(df):
    st.markdown('<div class="hero-kicker">Build v0.5 · Dashboard online</div>',
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

    # ---------------- Prediction Model ----------------
    st.markdown('<div class="section-title">Prediction Model</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">Accuracy alone is meaningless on an 80/20 split. '
        'Every metric here is measured against the honest baseline.</div>',
        unsafe_allow_html=True,
    )

    results = train_model(df)
    label, tone, explanation = results["verdict"]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        kpi_card("Model accuracy", f"{results['acc_model']*100:.1f}%",
                 "Random Forest, 4 features", tone="teal",
                 pct=int(results['acc_model']*100))
    with m2:
        kpi_card("Baseline accuracy", f"{results['acc_baseline']*100:.1f}%",
                 "always predict success", tone="gold",
                 pct=int(results['acc_baseline']*100))
    with m3:
        kpi_card("ROC-AUC", f"{results['auc']:.3f}",
                 f"cv: {results['cv_auc_mean']:.3f} ± {results['cv_auc_std']:.3f}",
                 tone="purple", pct=int(results['auc']*100))
    with m4:
        st.markdown(
            f'<div class="kpi {tone}">'
            f'<div class="kpi-label">Verdict</div>'
            f'<div style="margin-top:.5rem"><span class="badge {tone}">● {label}</span></div>'
            f'<div class="kpi-delta" style="margin-top:.6rem">{explanation}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="panel"><div class="panel-title">Model vs. Baseline</div>',
        unsafe_allow_html=True)
    max_val = max(results["acc_model"], results["acc_baseline"])
    st.markdown('<div class="honesty-label">Random Forest</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="honesty-bar"><div class="honesty-fill" '
        f'style="width:{results["acc_model"]/max_val*100}%;background:#2BD9C4">'
        f'{results["acc_model"]*100:.1f}%</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="honesty-label">Baseline (always predict success)</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="honesty-bar"><div class="honesty-fill" '
        f'style="width:{results["acc_baseline"]/max_val*100}%;background:#C9A227">'
        f'{results["acc_baseline"]*100:.1f}%</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="panel"><div class="panel-title">Try the predictor</div>',
        unsafe_allow_html=True)
    p1, p2 = st.columns(2)
    with p1:
        budget = st.slider("Budget ($M)", 1, 200, 50) * 1_000_000
        popularity = st.slider("Popularity", 1.0, 100.0, 50.0)
    with p2:
        runtime = st.slider("Runtime (min)", 80, 180, 120)
        vote_average = st.slider("Vote average", 3.0, 9.0, 6.5)

    proba = predict_one(results["model"], budget, popularity, runtime, vote_average)
    baseline_proba = results["acc_baseline"]
    delta = abs(proba - baseline_proba) * 100

    st.markdown(
        f'<div style="margin-top:1rem"><span class="badge teal">'
        f'● {proba*100:.1f}% predicted success</span></div>'
        f'<div class="kpi-delta" style="margin-top:.6rem">'
        f'Your inputs moved the estimate {delta:.1f} points from the base rate. '
        f'The model is reporting the base rate, not reading your film.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)