"""Dashboard — KPIs, EDA, model, and predictor, organized into tabs."""
import streamlit as st
from src.theme import kpi_card
from src.charts import (
    breakeven_scatter, genre_success_bar, correlation_heatmap,
    genre_share_donut, outcome_donut, budget_band_performance,
    distribution_histogram, genre_box, runtime_vs_rating_bubble,
)
from src.model import train_model, predict_one


def render(df):
    st.markdown('<div class="hero-kicker">Build v1.0 · Dashboard online</div>',
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

    st.write("")

    tab_overview, tab_genre, tab_dist, tab_model = st.tabs(
        ["📈 Overview", "🎬 Genre & Budget", "📊 Distributions", "🎯 Prediction Model"]
    )

    # ==================== TAB 1: OVERVIEW ====================
    with tab_overview:
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

        left2, right2 = st.columns([1, 1])
        with left2:
            st.markdown(
                '<div class="panel"><div class="panel-title">Profitable vs Loss</div>',
                unsafe_allow_html=True)
            st.plotly_chart(outcome_donut(df), use_container_width=True,
                             config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        with right2:
            st.markdown(
                '<div class="panel"><div class="panel-title">Success by Budget Category</div>',
                unsafe_allow_html=True)
            st.plotly_chart(budget_band_performance(df), use_container_width=True,
                             config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

    # ==================== TAB 2: GENRE & BUDGET ====================
    with tab_genre:
        left, right = st.columns([1.4, 1])
        with left:
            st.markdown(
                '<div class="panel"><div class="panel-title">Success Rate by Genre</div>',
                unsafe_allow_html=True)
            st.plotly_chart(genre_success_bar(df), use_container_width=True,
                             config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        with right:
            st.markdown(
                '<div class="panel"><div class="panel-title">Catalogue Share by Genre</div>',
                unsafe_allow_html=True)
            st.plotly_chart(genre_share_donut(df), use_container_width=True,
                             config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        st.markdown(
            '<div class="panel"><div class="panel-title">Runtime vs Rating, by Genre</div>'
            '<div style="color:#9089AB;font-size:.82rem;margin-bottom:.6rem">'
            'Bubble size is budget. If genres formed distinct clusters here, '
            'genre would carry real predictive signal — they don\'t.</div>',
            unsafe_allow_html=True)
        st.plotly_chart(runtime_vs_rating_bubble(df), use_container_width=True,
                         config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        left2, right2 = st.columns(2)
        with left2:
            st.markdown(
                '<div class="panel"><div class="panel-title">Runtime by Genre</div>',
                unsafe_allow_html=True)
            st.plotly_chart(genre_box(df, "runtime", "Runtime (min)"),
                             use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        with right2:
            st.markdown(
                '<div class="panel"><div class="panel-title">Rating by Genre</div>',
                unsafe_allow_html=True)
            st.plotly_chart(genre_box(df, "vote_average", "Vote average"),
                             use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

    # ==================== TAB 3: DISTRIBUTIONS ====================
    with tab_dist:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(
                '<div class="panel"><div class="panel-title">Budget Distribution</div>',
                unsafe_allow_html=True)
            st.plotly_chart(
                distribution_histogram(df, "budget", "Budget ($)", color="#9D5CFF",
                                       prefix="$", suffix=""),
                use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(
                '<div class="panel"><div class="panel-title">ROI Distribution</div>',
                unsafe_allow_html=True)
            st.plotly_chart(
                distribution_histogram(df, "roi", "ROI (multiplier)", color="#C9A227"),
                use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        c3, c4 = st.columns(2)
        with c3:
            st.markdown(
                '<div class="panel"><div class="panel-title">Runtime Distribution</div>',
                unsafe_allow_html=True)
            st.plotly_chart(
                distribution_histogram(df, "runtime", "Runtime (min)", color="#2BD9C4",
                                       suffix=" min"),
                use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)
        with c4:
            st.markdown(
                '<div class="panel"><div class="panel-title">Vote Average Distribution</div>',
                unsafe_allow_html=True)
            st.plotly_chart(
                distribution_histogram(df, "vote_average", "Vote average", color="#E0526B"),
                use_container_width=True, config={"displayModeBar": False})
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            '<div style="color:#5C5473;font-size:.78rem;margin-top:.8rem">'
            'Every distribution here is close to flat (uniform) rather than bell-shaped '
            'or skewed the way real-world film data would be — see Data Quality for '
            'the KS-test confirmation.</div>',
            unsafe_allow_html=True,
        )

    # ==================== TAB 4: PREDICTION MODEL ====================
    with tab_model:
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

        st.markdown("<div style='height:1.4rem'></div>", unsafe_allow_html=True)

        # ---- Historical range explorer (honest alternative to a "greenlight simulator") ----
        st.markdown(
            '<div class="panel"><div class="panel-title">Historical Range Explorer</div>'
            '<div style="color:#9089AB;font-size:.82rem;margin-bottom:.9rem">'
            'Not a prediction — the model above has no signal. This shows the '
            '<b>actual historical range</b> of similar films in this catalogue, for '
            'context when discussing a planned budget.</div>',
            unsafe_allow_html=True,
        )

        genre_options = sorted(df["genre"].unique())
        e1, e2 = st.columns(2)
        with e1:
            explore_genre = st.selectbox("Genre", genre_options, key="explore_genre")
        with e2:
            explore_budget = st.slider("Planned budget ($M)", 1, 250, 50,
                                       key="explore_budget")

        band_lo, band_hi = explore_budget * 0.6, explore_budget * 1.4
        similar = df[
            (df["genre"] == explore_genre)
            & (df["budget"] >= band_lo * 1e6)
            & (df["budget"] <= band_hi * 1e6)
        ]

        if len(similar) < 10:
            st.warning(
                f"Only {len(similar)} historical films fall within ±40% of this "
                f"budget for {explore_genre}. Widen the sidebar filters or try a "
                f"different budget for a more reliable range."
            )
        else:
            p25, p50, p75 = similar["revenue"].quantile([0.25, 0.5, 0.75]) / 1e6
            hist_success = similar["success"].mean()
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                kpi_card("HISTORICAL REVENUE RANGE (P25–P75)",
                         f"${p25:.0f}M – ${p75:.0f}M",
                         f"median ${p50:.0f}M", tone="purple", pct=60)
            with ec2:
                kpi_card("HISTORICAL SUCCESS RATE", f"{hist_success*100:.1f}%",
                         f"n = {len(similar)} similar films", tone="gold", pct=60)
            with ec3:
                kpi_card("CATALOGUE AVERAGE", f"{df['success'].mean()*100:.1f}%",
                         "all films, for comparison", tone="teal", pct=60)
            st.markdown(
                '<div style="color:#5C5473;font-size:.78rem;margin-top:.6rem">'
                'This range comes from films with similar genre and budget — it is '
                'a description of the past, not a forecast. The spread is wide '
                'because, per the model above, budget and genre do not reliably '
                'predict revenue in this dataset.</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)