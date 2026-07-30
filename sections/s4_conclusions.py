"""Section 06 — The Verdict / Conclusions.
Closes the loop on the brief's Reflection question: how confident would
you be in MovieIQ's answer, one limitation, one improvement.
"""
import streamlit as st


def render(df):
    st.markdown('<div class="hero-title" style="font-size:1.6rem">The Verdict</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">'
        'Insights, honest limitations, and where this project goes next.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="panel"><div class="panel-title">Key Insights</div>'
        '<ul style="color:#EDE9F5;font-size:.9rem;line-height:1.9;padding-left:1.2rem;margin:0">'
        '<li>None of the four usable features (budget, popularity, runtime, '
        'vote average) predict success — a Random Forest trained on all four '
        'scores no better than always guessing "success."</li>'
        '<li>The <code>vote_average</code> t-test and <code>genre</code> chi-square '
        'both fail to clear significance, even before correcting for multiple '
        'comparisons.</li>'
        '<li>Budget correlates strongly with raw revenue (structural, not '
        'predictive) but has essentially zero correlation with ROI — spending '
        'more does not buy a better return.</li>'
        '<li>A single film carries roughly a 1-in-5 chance of loss that no '
        'feature reduces. A diversified slate narrows that risk considerably, '
        'without changing the odds of any one film.</li>'
        '</ul></div>',
        unsafe_allow_html=True,
    )

    st.write("")

    st.markdown(
        '<div class="panel"><div class="panel-title">Reflection</div>'
        '<div style="color:#EDE9F5;font-size:.92rem;line-height:1.8">'
        'If a studio asked whether their next film will succeed, MovieIQ\'s '
        'honest answer is the base rate — and it would give that same answer '
        'for every film ever made. The model has no discriminative power '
        '(ROC-AUC ≈ 0.51, against a 0.50 coin flip), because the dataset\'s '
        'features are statistically independent of the outcome.<br><br>'
        '<b>Limitation:</b> the data itself, not the algorithm. Budget, '
        'runtime, popularity, and vote average say nothing about commercial '
        'performance — and the variables that plausibly would (cast, release '
        'window, marketing spend, competing titles, franchise status, '
        'critical reception at release) are absent from this file.<br><br>'
        '<b>What MovieIQ can still do:</b> size the risk. A single film '
        'carries a real chance of loss that no feature changes — but a '
        'diversified slate is far more reliably profitable, which the Risk '
        'Room shows directly from this same data.<br><br>'
        '<b>Improvement, given more time:</b> join this dataset with real '
        'sources — TMDB and Box Office Mojo — to obtain the missing '
        'predictors, and re-run this analysis on real releases rather than '
        'synthetic ones. I would expect the honesty meter to finally read '
        'PREDICTIVE.'
        '</div></div>',
        unsafe_allow_html=True,
    )