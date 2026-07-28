"""Section 03 — Statistical Tests. Brief Stage 3.
Renders the t-test and chi-square results from src/stats_lab.py,
plus a plain-language explanation of what a p-value means.
"""
import streamlit as st
from src.theme import kpi_card
from src.stats_lab import (
    run_ttest,
    run_chi_square,
    verdict,
    bonferroni_alpha,
    ALPHA_DEFAULT,
)


def _verdict_badge(p_value: float, alpha: float) -> str:
    is_sig = p_value < alpha
    tone = "teal" if is_sig else "gold"
    text = verdict(p_value, alpha)
    return f'<span class="badge {tone}">● {text}</span>'


def render(df):
    st.markdown('<div class="hero-title" style="font-size:1.6rem">The Lab</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">'
        'Two hypothesis tests, run live on the data. '
        'Each answers one question: does this feature actually tell us '
        'anything about whether a film succeeds?'
        '</div>',
        unsafe_allow_html=True,
    )

    alpha = st.slider(
        "Significance threshold (α)",
        min_value=0.001, max_value=0.10, value=ALPHA_DEFAULT, step=0.001,
        format="%.3f",
    )
    bonferroni_toggle = st.checkbox(
        "Apply Bonferroni correction (2 tests run on this page)", value=False
    )
    effective_alpha = bonferroni_alpha(alpha, 2) if bonferroni_toggle else alpha

    st.caption(
        f"Testing at α = {effective_alpha:.4f}"
        + (" (Bonferroni-corrected)" if bonferroni_toggle else "")
    )

    # ---- T-TEST ----
    t = run_ttest(df, feature="vote_average")
    st.markdown(
        '<div class="panel">'
        '<div class="panel-title">T-Test — Vote Average by Success</div>'
        '<div style="color:#EDE9F5;font-size:.9rem;margin-bottom:1rem">'
        '<b>Null hypothesis:</b> the mean <code>vote_average</code> is the same for '
        'successful and unsuccessful films.</div>'
        '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem">'
        f'<div class="kpi teal" style="flex:1;min-width:180px">'
        f'<div class="kpi-label">SUCCESS GROUP MEAN</div>'
        f'<div class="kpi-value">{t["group1_mean"]:.2f}</div>'
        f'<div class="kpi-delta">n = {t["group1_n"]}</div></div>'
        f'<div class="kpi purple" style="flex:1;min-width:180px">'
        f'<div class="kpi-label">FAILURE GROUP MEAN</div>'
        f'<div class="kpi-value">{t["group0_mean"]:.2f}</div>'
        f'<div class="kpi-delta">n = {t["group0_n"]}</div></div>'
        f'<div class="kpi gold" style="flex:1;min-width:180px">'
        f'<div class="kpi-label">T-STATISTIC</div>'
        f'<div class="kpi-value">{t["t_stat"]:.3f}</div>'
        f'<div class="kpi-delta">p = {t["p_value"]:.4f}</div></div>'
        '</div>'
        f'{_verdict_badge(t["p_value"], effective_alpha)}'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    # ---- CHI-SQUARE ----
    c = run_chi_square(df, feature="genre")
    st.markdown(
        '<div class="panel">'
        '<div class="panel-title">Chi-Square — Genre vs Success</div>'
        '<div style="color:#EDE9F5;font-size:.9rem;margin-bottom:1rem">'
        '<b>Null hypothesis:</b> <code>genre</code> and <code>success</code> are independent — '
        'knowing the genre tells you nothing about the odds of success.</div>'
        '<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem">'
        f'<div class="kpi purple" style="flex:1;min-width:180px">'
        f'<div class="kpi-label">CHI-SQUARE STATISTIC</div>'
        f'<div class="kpi-value">{c["chi2_stat"]:.3f}</div>'
        f'<div class="kpi-delta">dof = {c["dof"]}</div></div>'
        f'<div class="kpi gold" style="flex:1;min-width:180px">'
        f'<div class="kpi-label">P-VALUE</div>'
        f'<div class="kpi-value">{c["p_value"]:.4f}</div>'
        f'<div class="kpi-delta">&nbsp;</div></div>'
        '</div>'
        f'{_verdict_badge(c["p_value"], effective_alpha)}'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.expander("View contingency table (genre × success)"):
        st.dataframe(c["contingency_table"], use_container_width=True)

    st.write("")

    # ---- PLAIN-LANGUAGE P-VALUE EXPLANATION ----
    st.markdown('<div class="panel"><div class="panel-title">What a p-value actually means</div>', unsafe_allow_html=True)
    st.markdown(
        "A p-value is the probability of seeing a result at least this "
        "extreme **if the null hypothesis were true** — i.e. if the "
        "feature genuinely had no relationship to success and the "
        "pattern we observed were pure chance.\n\n"
        f"We're using α = **{alpha:.3f}** as the cutoff: if p is below "
        "that, the result is unlikely enough to happen by chance alone "
        "that we call it statistically significant. Above it, we can't "
        "rule out chance as the explanation.\n\n"
        "Neither test here clears that bar in a way that survives "
        "scrutiny — `vote_average` comes nowhere close (p = "
        f"{t['p_value']:.3f}), and `genre` is even further from it "
        f"(p = {c['p_value']:.3f}). That's consistent with the honesty "
        "meter on the Greenlight Engine page: this dataset's features "
        "carry effectively no signal about which films succeed."
    )
    st.markdown("</div>", unsafe_allow_html=True)