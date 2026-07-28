"""Section 05 — The Risk Room / Risk Simulator.
Break-even simulator and slate diversification builder.
Answers the question the classifier could not: how much capital
should be at risk, across how many titles?
"""
import streamlit as st
from src.theme import kpi_card
from src.charts import profit_distribution_chart, slate_roi_chart
from src.simulate import simulate_breakeven, simulate_slate_roi, MAX_DRAWS


def render(df):
    st.markdown('<div class="hero-title" style="font-size:1.6rem">The Risk Room</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">'
        'The model has no discriminative power over single films — but risk '
        'can still be sized. These tools draw revenue multipliers empirically '
        'from the films currently in view, then simulate outcomes.'
        '</div>',
        unsafe_allow_html=True,
    )

    if len(df) < 30:
        st.warning(
            f"Only {len(df)} films in view — too few to simulate reliably. "
            "Widen the sidebar filters for a more stable result."
        )
        return

    # ---------------- Break-Even Simulator ----------------
    st.markdown('<div class="section-title" style="font-size:1.2rem;margin-top:0">Break-Even Simulator</div>',
                unsafe_allow_html=True)

    budget_m = st.slider("Budget ($M)", 1, 250, 80)
    budget = budget_m * 1_000_000

    result = simulate_breakeven(df, budget, n_draws=MAX_DRAWS, seed=42)

    st.markdown(
        f'<div class="panel">'
        f'<div class="panel-title">Break-Even Simulator — ${budget_m}M production</div>'
        f'<div style="color:#9089AB;font-size:.82rem;margin-bottom:1rem">'
        f'{result["n_draws"]:,} Monte Carlo draws from the empirical revenue multiplier '
        f'({len(df):,} films in view).</div>'
        f'<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem">'
        f'<div class="kpi teal" style="flex:1;min-width:160px">'
        f'<div class="kpi-label">P(PROFIT)</div>'
        f'<div class="kpi-value">{result["p_profit"]*100:.1f}%</div></div>'
        f'<div class="kpi gold" style="flex:1;min-width:160px">'
        f'<div class="kpi-label">EXPECTED PROFIT</div>'
        f'<div class="kpi-value">${result["expected_profit"]/1e6:+.1f}M</div></div>'
        f'<div class="kpi red" style="flex:1;min-width:160px">'
        f'<div class="kpi-label">5% VAR</div>'
        f'<div class="kpi-value">${result["var_5"]/1e6:+.1f}M</div>'
        f'<div class="kpi-delta">worst 1-in-20</div></div>'
        f'<div class="kpi purple" style="flex:1;min-width:160px">'
        f'<div class="kpi-label">BREAK-EVEN REV.</div>'
        f'<div class="kpi-value">${budget_m}M</div></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    left, right = st.columns([1.6, 1])
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Simulated Profit Distribution</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(profit_distribution_chart(result["profits"]),
                         use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        p = result["percentiles"]
        st.markdown(
            '<div class="panel"><div class="panel-title">Percentile Ladder</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:.85rem;line-height:2.1">'
            f'<span style="color:#E0526B">P05  ${p[5]/1e6:+.1f}M</span><br>'
            f'<span style="color:#9089AB">P25  ${p[25]/1e6:+.1f}M</span><br>'
            f'<span style="color:#EDE9F5">P50  ${p[50]/1e6:+.1f}M</span><br>'
            f'<span style="color:#9089AB">P75  ${p[75]/1e6:+.1f}M</span><br>'
            f'<span style="color:#2BD9C4">P95  ${p[95]/1e6:+.1f}M</span>'
            f'</div>'
            '<div style="color:#5C5473;font-size:.78rem;margin-top:.8rem">'
            'The table an investor reads first.</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    st.write("")

    # ---------------- Slate Builder ----------------
    st.markdown('<div class="section-title" style="font-size:1.2rem">Slate Builder</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">'
        'A single film carries the loss chance shown above and nothing reduces it. '
        'A portfolio behaves differently — set a slate size to see how.'
        '</div>',
        unsafe_allow_html=True,
    )

    slate_size = st.slider("Slate size (films)", 1, 30, 5)

    reference_sizes = sorted(set([1, 5, 20, slate_size]))
    roi_dict = {size: simulate_slate_roi(df, size, n_portfolios=MAX_DRAWS, seed=42)
                for size in reference_sizes}

    user_roi = roi_dict[slate_size]
    p_profit_slate = float((user_roi > 0).mean())

    c1, c2 = st.columns(2)
    with c1:
        kpi_card(f"P(SLATE PROFITABLE) — {slate_size} FILMS",
                 f"{p_profit_slate*100:.1f}%", "", tone="teal", pct=int(p_profit_slate*100))
    with c2:
        kpi_card("EXPECTED PORTFOLIO ROI", f"{user_roi.mean()*100:+.1f}%",
                 "", tone="gold", pct=60)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="panel"><div class="panel-title">Diversification, Simulated</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(slate_roi_chart(roi_dict), use_container_width=True,
                     config={"displayModeBar": False})
    st.markdown(
        '<div style="color:#9089AB;font-size:.82rem">'
        'This is why studios greenlight slates rather than single films — '
        'a wider slate does not change the odds of any one film, but it '
        'tightens the range of the portfolio\'s overall outcome.'
        '</div></div>',
        unsafe_allow_html=True,
    )