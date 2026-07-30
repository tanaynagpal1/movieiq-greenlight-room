"""Section — Project Report.
The report is built once as a list of content blocks, then rendered three
ways: inline in Streamlit, as Markdown, and as a themed PDF. One source of
truth means the download and the screen can never disagree.
"""
import re

import numpy as np
import streamlit as st

from src.audit import run_checks, health_score
from src.stats_lab import run_ttest, run_chi_square
from src.model import train_model
from src.simulate import simulate_breakeven, simulate_slate_roi
from src.charts import (
    breakeven_scatter, correlation_heatmap, genre_success_bar,
    profit_distribution_chart, slate_roi_chart,
)
from src import mpl_charts
from src.pdf_report import build_pdf


def _md_inline(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<i>\1</i>", text)
    return text


def _to_markdown(doc):
    out = []
    for kind, content in doc:
        if kind == "h2":
            out.append(f"\n## {content}\n")
        elif kind == "h3":
            out.append(f"### {content}\n")
        elif kind == "p":
            out.append(content + "\n")
        elif kind == "ul":
            out.extend(f"- {i}" for i in content)
            out.append("")
        elif kind == "kpis":
            out.extend(f"- {label}: {value}" for label, value in content)
            out.append("")
        elif kind == "img":
            out.append(f"*Figure — {content[0]}*\n")
    return "\n".join(out)


class _Doc:
    """Builds the block list while rendering each block to Streamlit."""

    def __init__(self):
        self.blocks = []

    def heading(self, num, text):
        title = f"{num}. {text}"
        st.markdown(f'<div class="section-title" style="font-size:1.15rem">'
                    f'{num} &middot; {text}</div>', unsafe_allow_html=True)
        self.blocks.append(("h2", title))

    def panel(self, title, parts):
        """parts: list of ("p", text) or ("ul", [items])."""
        body = ""
        for kind, content in parts:
            if kind == "p":
                body += f'<p style="margin:0 0 .85rem">{_md_inline(content)}</p>'
            else:
                items = "".join(f"<li>{_md_inline(i)}</li>" for i in content)
                body += (f'<ul style="padding-left:1.2rem;margin:0 0 .85rem">'
                         f'{items}</ul>')
        st.markdown(
            f'<div class="panel"><div class="panel-title">{title}</div>'
            f'<div style="color:#EDE9F5;font-size:.9rem;line-height:1.8">{body}</div>'
            f'</div>', unsafe_allow_html=True)
        st.write("")
        self.blocks.append(("h3", title))
        self.blocks.extend(parts)

    def kpis(self, items):
        """items: list of (label, value, tone)."""
        cells = "".join(
            f'<div class="kpi {tone}" style="flex:1;min-width:150px">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div></div>'
            for label, value, tone in items)
        st.markdown(f'<div style="display:flex;gap:1rem;flex-wrap:wrap;'
                    f'margin-bottom:1rem">{cells}</div>', unsafe_allow_html=True)
        self.blocks.append(("kpis", [(l, v) for l, v, _ in items]))

    def chart(self, title, fig, caption, png_getter):
        st.markdown(f'<div class="panel"><div class="panel-title">{title}</div>',
                    unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown(f'<div style="color:#9089AB;font-size:.82rem">'
                    f'{_md_inline(caption)}</div></div>', unsafe_allow_html=True)
        st.write("")
        self.blocks.append(("img", (f"{title}. {caption}", png_getter)))


def render(df, raw_df):
    doc = _Doc()

    st.markdown('<div class="hero-title" style="font-size:1.6rem">Project Report</div>',
                unsafe_allow_html=True)
    st.markdown('<div class="section-sub">'
                'A complete report on the active dataset. The business framing is '
                'fixed; every figure, chart and recommendation is recomputed from the '
                'data currently loaded. The controls below are live.'
                '</div>', unsafe_allow_html=True)

    source = st.session_state.get("file_name", "movies.csv (bundled)")
    st.markdown(f'<div style="font-size:.78rem;color:#5C5473;margin-bottom:1.2rem">'
                f'Report generated from: <span style="font-family:\'JetBrains Mono\','
                f'monospace;color:#C9A227">{source}</span> · {len(df):,} rows</div>',
                unsafe_allow_html=True)

    # ---------------- 1 · THEORY ----------------
    doc.heading(1, "Business Framing")

    doc.panel("Business problem", [
        ("p", "Film production is a capital-intensive business with highly uncertain "
              "returns. A single title can absorb tens or hundreds of millions of "
              "dollars before a ticket is sold, and the decision to greenlight is "
              "usually made on instinct, precedent and relationships rather than "
              "measured evidence. The core problem is that studios and investors "
              "commit capital without a quantified view of the downside they accept."),
    ])

    doc.panel("Business objective", [
        ("p", "Determine whether commercial success can be predicted from pre-release "
              "characteristics available at greenlight time — budget, popularity, "
              "runtime, average audience rating and genre — and if it can, build a "
              "tool that supports the decision. Success is defined precisely as "
              "**revenue exceeding budget**, making this a binary classification "
              "problem."),
        ("p", "Where prediction proves unreliable, the secondary objective is to "
              "quantify and communicate the *risk* attached to a production, so "
              "capital can be sized responsibly even without a predictive signal."),
    ])

    doc.panel("Stakeholders", [
        ("ul", [
            "**Studios and production companies** — decide which projects to "
            "greenlight and at what budget, and need to understand loss exposure per "
            "title.",
            "**Investors and financiers** — need downside estimates, break-even "
            "thresholds and portfolio-level risk before committing funds.",
            "**Distributors and streaming platforms** — need a view on which titles "
            "justify acquisition spend.",
            "**Analysts and data teams** — need an honest, reproducible assessment "
            "rather than a headline accuracy figure that flatters the model.",
        ]),
    ])

    doc.panel("Methodology — what we did, and why", [
        ("ul", [
            "**Data audit before analysis.** Twelve automated quality checks run on "
            "load, before any modelling. Reason: conclusions from unexamined data are "
            "unreliable regardless of technique, and problems like hidden missingness "
            "or target leakage are invisible in summary statistics.",
            "**Exploratory analysis.** Distributions, correlations and a break-even "
            "view of budget against revenue. Reason: to see the shape of the data and "
            "identify relationships worth testing formally.",
            "**Formal statistical testing.** A t-test on a continuous feature and a "
            "chi-square test on a categorical one. Reason: visual patterns can be "
            "coincidence — hypothesis tests attach a probability to that possibility.",
            "**Predictive modelling judged against a baseline.** A Random Forest, with "
            "accuracy always reported beside the majority-class baseline and ROC-AUC. "
            "Reason: on an imbalanced target, raw accuracy is misleading — a model "
            "that always guesses the majority class can look strong while carrying no "
            "information.",
            "**Risk quantification via Monte Carlo simulation.** Revenue multipliers "
            "resampled from the data to simulate outcomes for one film and for slates. "
            "Reason: when prediction fails, sizing risk is still valuable — and "
            "portfolio behaviour differs sharply from single-title behaviour.",
        ]),
    ])

    # ---------------- 2 · PROFILE ----------------
    doc.heading(2, "Dataset Profile")

    success_rate = df["success"].mean()
    n_genres = df["genre"].nunique()
    median_roi = df["roi"].median()

    doc.kpis([
        ("Rows", f"{len(df):,}", "purple"),
        ("Success rate", f"{success_rate*100:.1f}%", "gold"),
        ("Genres", f"{n_genres}", "teal"),
        ("Median ROI", f"{median_roi*100:+.1f}%", "red"),
    ])

    minority = min(success_rate, 1 - success_rate)
    majority = max(success_rate, 1 - success_rate)
    balance_note = (
        f"The target is **imbalanced**: the minority class is only "
        f"{minority*100:.1f}% of rows. This is the most important fact for "
        f"interpreting accuracy — always predicting the majority class would score "
        f"{majority*100:.1f}% without learning anything."
        if minority < 0.35 else
        f"The target is reasonably **balanced** ({success_rate*100:.1f}% success), so "
        f"accuracy is more meaningful here than on a skewed target — though it is "
        f"still reported against the baseline below.")

    doc.panel("Composition and class balance", [
        ("p", f"The active dataset contains {len(df):,} films across {n_genres} genre "
              f"labels. {success_rate*100:.1f}% are successful by the "
              f"revenue-exceeds-budget definition. Median return on budget is "
              f"{median_roi*100:+.1f}%."),
        ("p", balance_note),
    ])

    # ---------------- 3 · PREPARATION ----------------
    doc.heading(3, "Data Preparation")

    checks = run_checks(raw_df)
    score = health_score(checks)
    n_pass = sum(1 for c in checks if c["verdict"] == "pass")
    n_flag = sum(1 for c in checks if c["verdict"] == "flag")
    n_crit = sum(1 for c in checks if c["verdict"] == "critical")
    flagged = [c for c in checks if c["verdict"] in ("flag", "critical")]

    doc.kpis([
        ("Health score", f"{score}/100",
         "teal" if score >= 80 else "gold" if score >= 60 else "red"),
        ("Passed", f"{n_pass}", "teal"),
        ("Flagged", f"{n_flag}", "gold"),
        ("Critical", f"{n_crit}", "red"),
    ])

    flagged_items = [f"**{c['name']}** — {c['result']}. {c['note']}" for c in flagged] \
        or ["No issues were flagged by the audit."]

    doc.panel("What the audit found", [
        ("p", f"Twelve checks scored the raw file at **{score}/100** "
              f"({n_pass} passed, {n_flag} flagged, {n_crit} critical). Issues raised:"),
        ("ul", flagged_items),
    ])

    doc.panel("Cleaning decisions, and the reasoning", [
        ("ul", [
            "**Genre parsing** — the genres field holds a stringified Python list, so "
            "it was parsed with `ast.literal_eval` inside a try/except and the first "
            "genre taken. Not `json.loads`: the quoting is single, which JSON rejects.",
            "**Empty genre lists relabelled Unspecified, not dropped** — these parse "
            "without error, so `isnull()` never sees them. They were kept because "
            "their success rate closely matches the labelled rows, indicating "
            "missingness is random rather than informative.",
            "**vote_average rounded for display only** — excess decimal precision is "
            "an artefact, but full precision was retained for modelling so no "
            "information is lost.",
            "**revenue excluded from every feature matrix** — the target is derived "
            "from revenue, so including it would leak the answer.",
            "**No rows dropped** — a defensible nothing-removed is a stronger position "
            "than unexplained deletions.",
        ]),
    ])

    # ---------------- 4 · EDA ----------------
    doc.heading(4, "Exploratory Findings")

    corr_br = df["budget"].corr(df["revenue"])
    corr_broi = df["budget"].corr(df["roi"])

    doc.panel("Budget, revenue and the return trap", [
        ("p", f"Budget and revenue correlate at r = {corr_br:+.2f}, which looks like a "
              f"strong finding and is where most analyses stop. It is misleading: "
              f"revenue scales with budget by construction — a $200M film returning "
              f"$220M has large absolute revenue and a terrible 10% return. The "
              f"decision-relevant question is return, not size. Budget correlates with "
              f"the ROI multiplier at r = {corr_broi:+.3f}"
              + (", effectively zero: spending more does not buy a better return."
                 if abs(corr_broi) < 0.10 else
                 ", a relationship worth investigating further.")),
    ])

    doc.chart("Budget vs revenue, with break-even line", breakeven_scatter(df),
              "Everything below the gold 45-degree line lost money. The wedge shape is "
              "the signature of revenue being a multiple of budget.",
              lambda: mpl_charts.breakeven_scatter_png(df))

    genre_rates = df.groupby("genre")["success"].agg(["mean", "count"])
    genre_rates = genre_rates[genre_rates["count"] >= 10].sort_values("mean")
    if len(genre_rates) >= 2:
        spread = (genre_rates["mean"].iloc[-1] - genre_rates["mean"].iloc[0]) * 100
        best, worst = genre_rates.index[-1], genre_rates.index[0]
        genre_text = (
            f"Success rates by genre span {spread:.1f} percentage points, from {worst} "
            f"at the low end to {best} at the high end."
            + (" That spread is narrow enough to be consistent with random variation "
               "rather than a genuine genre effect." if spread < 10 else
               " That spread is wide enough to warrant treating genre as a real factor."))
    else:
        genre_text = "Too few genres with sufficient sample size to compare rates."

    doc.panel("Genre", [("p", genre_text)])
    doc.chart("Success rate by genre", genre_success_bar(df),
              "Bars clustered near the overall average indicate genre carries little "
              "information about success.",
              lambda: mpl_charts.genre_success_bar_png(df))

    doc.chart("Correlation matrix", correlation_heatmap(df),
              "The only strong pair is budget with revenue, which is structural. "
              "Revenue is excluded from the model as leakage, so that pair never "
              "enters the feature matrix and multicollinearity is not a concern.",
              lambda: mpl_charts.correlation_heatmap_png(df))

    # ---------------- 5 · STATISTICS ----------------
    doc.heading(5, "Statistical Testing")

    alpha = st.slider("Significance threshold (α)", 0.001, 0.10, 0.05, step=0.001,
                      format="%.3f", key="report_alpha")
    bonf = alpha / 2
    st.caption(f"Two tests are run, so the Bonferroni-corrected threshold is "
               f"α = {bonf:.4f}.")

    t = run_ttest(df, feature="vote_average")
    c = run_chi_square(df, feature="genre")
    t_sig, c_sig = t["p_value"] < alpha, c["p_value"] < alpha

    doc.kpis([
        ("T-statistic", f"{t['t_stat']:.3f}", "purple"),
        ("T-test p", f"{t['p_value']:.4f}", "teal" if t_sig else "gold"),
        ("Chi-square", f"{c['chi2_stat']:.3f}", "purple"),
        ("Chi-square p", f"{c['p_value']:.4f}", "teal" if c_sig else "gold"),
    ])

    def _verdict(p, sig):
        if sig and p < bonf:
            return (f"significant at alpha = {alpha:.3f} (p = {p:.4f}) and it survives "
                    f"the Bonferroni correction (alpha = {bonf:.4f})")
        if sig:
            return (f"significant at alpha = {alpha:.3f} (p = {p:.4f}) but it fails "
                    f"the Bonferroni correction (alpha = {bonf:.4f}) — a fragile "
                    f"result that should not be reported as a finding on its own")
        return (f"not significant (p = {p:.4f}); we cannot reject the null hypothesis "
                f"that it carries no relationship to success")

    doc.panel("Hypothesis tests and what they mean", [
        ("p", f"**Test 1 — t-test on average audience rating.** Null hypothesis: mean "
              f"`vote_average` is identical for successful and unsuccessful films. The "
              f"result is {_verdict(t['p_value'], t_sig)}. Group means were "
              f"{t['group1_mean']:.2f} (successful, n = {t['group1_n']}) versus "
              f"{t['group0_mean']:.2f} (unsuccessful, n = {t['group0_n']})."),
        ("p", f"**Test 2 — chi-square on genre.** Null hypothesis: genre and success "
              f"are independent. The result is {_verdict(c['p_value'], c_sig)} "
              f"(chi-squared = {c['chi2_stat']:.3f}, dof = {c['dof']})."),
        ("p", "**Why a correction is applied.** Running multiple tests inflates the "
              "chance that at least one clears the threshold by luck alone. Dividing "
              "the threshold by the number of tests holds the family-wise error rate "
              "at the intended level. Reporting an uncorrected borderline result as a "
              "discovery is one of the most common analytical errors."),
    ])

    # ---------------- 6 · MODEL ----------------
    doc.heading(6, "Predictive Modelling")

    results = None
    if df["success"].nunique() < 2:
        st.warning("The active dataset contains only one outcome class, so no "
                   "classifier can be trained.")
        doc.panel("Model not trained", [
            ("p", "The active dataset contains only one outcome class, so no "
                  "classifier could be trained.")])
    elif len(df) < 50:
        st.warning(f"Only {len(df)} rows — too few to train and evaluate a classifier "
                   f"meaningfully.")
        doc.panel("Model not trained", [
            ("p", f"Only {len(df)} rows were available — too few to train and "
                  f"evaluate a classifier meaningfully.")])
    else:
        results = train_model(df)

    if results is not None:
        label, tone, _expl = results["verdict"]
        lift = results["acc_model"] - results["acc_baseline"]
        top_feat = max(results["importances"], key=results["importances"].get)

        doc.kpis([
            ("Model accuracy", f"{results['acc_model']*100:.1f}%", "teal"),
            ("Baseline", f"{results['acc_baseline']*100:.1f}%", "gold"),
            ("ROC-AUC", f"{results['auc']:.3f}", "purple"),
            ("Verdict", label, tone),
        ])

        base = (f"The Random Forest scored {results['acc_model']*100:.1f}% accuracy "
                f"against a majority-class baseline of "
                f"{results['acc_baseline']*100:.1f}% — a lift of {lift*100:+.1f} "
                f"percentage points. ROC-AUC is {results['auc']:.3f} against 0.500 for "
                f"a coin flip, with cross-validated AUC of "
                f"{results['cv_auc_mean']:.3f} +/- {results['cv_auc_std']:.3f}.")

        if label == "NO SIGNAL":
            tail = ("**The model carries no usable signal.** Reporting the accuracy "
                    "figure alone would imply a working predictor; measured against "
                    "the only honest yardstick, it does not beat guessing. This is a "
                    "finding about the data, not a failure of the algorithm — the "
                    "available features are statistically independent of the outcome, "
                    "which the hypothesis tests above independently confirm.")
        elif label == "MARGINAL":
            tail = (f"**The edge is real but small enough to sit within noise.** It "
                    f"should not drive individual decisions without validation on "
                    f"held-out data from a different period. The most informative "
                    f"feature was `{top_feat}`.")
        else:
            tail = (f"**The model beats the baseline by a meaningful margin**, so the "
                    f"features carry genuine information about success. The most "
                    f"informative feature was `{top_feat}`. Before operational use it "
                    f"should be validated on data from a period the model has not "
                    f"seen, to confirm the relationship is stable over time.")

        doc.panel("Model setup and honest evaluation", [
            ("p", "Features: budget, popularity, runtime and average rating. `revenue` "
                  "and `title` were excluded — revenue defines the target (leakage) "
                  "and title is a unique identifier carrying no generalisable "
                  "information. Split: 80/20, stratified to preserve the class ratio "
                  "in both halves, with a fixed seed for reproducibility."),
            ("p", base),
            ("p", tail),
        ])

    # ---------------- 7 · RISK ----------------
    doc.heading(7, "Risk Assessment")

    sim = None
    p20 = None
    if len(df) < 30:
        st.warning("Too few rows to simulate risk reliably.")
        doc.panel("Simulation skipped", [
            ("p", "Too few rows in the active dataset to simulate risk reliably.")])
    else:
        default_budget = int(min(max(df["budget"].median() / 1e6, 1), 250))
        budget_m = st.slider("Production budget for the simulation ($M)", 1, 250,
                             default_budget, key="report_budget")
        ref_budget = budget_m * 1_000_000

        sim = simulate_breakeven(df, ref_budget, seed=42)
        roi_1 = simulate_slate_roi(df, 1, seed=42)
        roi_5 = simulate_slate_roi(df, 5, seed=42)
        roi_20 = simulate_slate_roi(df, 20, seed=42)
        p1 = float((roi_1 > 0).mean())
        p20 = float((roi_20 > 0).mean())

        doc.kpis([
            ("P(profit), 1 film", f"{sim['p_profit']*100:.1f}%", "teal"),
            ("Expected profit", f"${sim['expected_profit']/1e6:+.1f}M", "gold"),
            ("5% VaR", f"${sim['var_5']/1e6:+.1f}M", "red"),
            ("P(profit), 20 films", f"{p20*100:.1f}%", "purple"),
        ])

        doc.panel("Simulated exposure, and why diversification is the recommendation", [
            ("p", f"Revenue multipliers were resampled from the active dataset "
                  f"({sim['n_draws']:,} draws) to simulate outcomes for a film at a "
                  f"${budget_m}M budget. Reason for resampling rather than assuming a "
                  f"distribution: the empirical spread is the best available "
                  f"description of how returns actually behave in this data."),
            ("p", f"A single production at that budget carries a "
                  f"{sim['p_profit']*100:.1f}% chance of profit, an expected outcome "
                  f"of ${sim['expected_profit']/1e6:+.1f}M, and a 5% value-at-risk of "
                  f"${sim['var_5']/1e6:+.1f}M — a one-in-twenty chance of losing at "
                  f"least that much. Percentile outcomes run from "
                  f"${sim['percentiles'][5]/1e6:+.1f}M at P05 to "
                  f"${sim['percentiles'][95]/1e6:+.1f}M at P95."),
            ("p", f"**Portfolio effect.** A single film is profitable in "
                  f"{p1*100:.1f}% of simulations; a twenty-film slate in "
                  f"{p20*100:.1f}%. Diversification does not change the odds on any "
                  f"individual title — it narrows the distribution of the aggregate "
                  f"outcome. This is the quantitative case for greenlighting slates "
                  f"rather than one-off productions."),
        ])

        doc.chart(f"Simulated profit distribution at ${budget_m}M",
                  profit_distribution_chart(sim["profits"]),
                  "Red outcomes lost money. The gold line marks break-even.",
                  lambda p=sim["profits"]: mpl_charts.profit_distribution_png(p))

        doc.chart("Diversification, simulated",
                  slate_roi_chart({1: roi_1, 5: roi_5, 20: roi_20}),
                  "One film is a wide, flat distribution with a fat left tail. Twenty "
                  "films is tight and reliably above break-even.",
                  lambda d={1: roi_1, 5: roi_5, 20: roi_20}: mpl_charts.slate_roi_png(d))

    # ---------------- 8 · INSIGHTS ----------------
    doc.heading(8, "Insights and Recommendations")

    insights = []
    if results is not None and results["verdict"][0] == "NO SIGNAL":
        insights.append(
            "Pre-release characteristics in this dataset do not predict commercial "
            "success. Any greenlight tool built on them alone would be reporting the "
            "base rate while appearing to make a prediction.")
    elif results is not None:
        insights.append(
            f"The available features carry "
            f"{'some' if results['verdict'][0] == 'MARGINAL' else 'genuine'} "
            f"predictive information about success, with ROC-AUC {results['auc']:.3f}.")
    if not t_sig and not c_sig:
        insights.append(
            "Neither the continuous nor the categorical feature tested shows a "
            "statistically significant relationship with success, which corroborates "
            "the modelling result rather than contradicting it.")
    if abs(corr_broi) < 0.10:
        insights.append(
            f"Budget size is uncorrelated with return (r = {corr_broi:+.3f}). Larger "
            f"productions generate larger revenue but not better returns — the "
            f"budget-revenue correlation measures scale, not skill.")
    if sim is not None:
        insights.append(
            f"Risk is quantifiable even where prediction is not: at the simulated "
            f"budget a production carries a {(1-sim['p_profit'])*100:.1f}% chance of "
            f"loss, while a twenty-film slate is profitable in {p20*100:.1f}% of "
            f"simulations.")

    recommendations = []
    if results is not None and results["verdict"][0] == "NO SIGNAL":
        recommendations.append(
            "**Do not use this model for greenlight decisions.** Use it as evidence "
            "that these variables are insufficient, and as a baseline a better-sourced "
            "model must beat.")
        recommendations.append(
            "**Shift the question from selection to sizing.** Since individual "
            "outcomes cannot be predicted, manage exposure: cap single-title budgets "
            "relative to total capital and plan at slate level.")
    elif results is not None:
        recommendations.append(
            "**Validate before operational use.** Confirm the model holds on data "
            "from a period it has not seen before letting it influence spend.")
    recommendations.append(
        "**Greenlight slates, not single films.** The simulation shows portfolio "
        "construction converts an uncertain individual bet into a far more reliable "
        "aggregate outcome.")
    recommendations.append(
        "**Acquire the variables that plausibly matter.** Cast and director track "
        "record, release window and competing titles, marketing spend, franchise "
        "status and critical reception at release are absent here and are the most "
        "likely sources of real predictive signal.")
    recommendations.append(
        "**Always report accuracy against a baseline.** On an imbalanced target, a "
        "lone accuracy figure can conceal a model that has learned nothing.")

    doc.panel("Insights", [("ul", insights)])
    doc.panel("Recommendations", [("ul", recommendations)])

    doc.panel("Limitations", [
        ("p", "The analysis is bounded by the columns supplied. Features known to "
              "influence commercial performance — cast, marketing spend, release "
              "timing, competitive context, franchise status, critical reception — are "
              "absent, so the finding concerns these variables specifically, not film "
              "success being inherently unpredictable."),
        ("p", "The risk simulation resamples historical multipliers and therefore "
              "assumes future returns resemble those observed. Structural change in "
              "the market would invalidate that assumption."),
        ("p", "Success is defined as revenue exceeding production budget. This "
              "excludes marketing and distribution costs, so it understates the true "
              "break-even point of a real production."),
    ])

    # ---------------- EXPORT ----------------
    st.markdown('<div class="panel"><div class="panel-title">Export</div>'
                '<div style="color:#9089AB;font-size:.85rem">'
                'Download this report with the figures above baked in as they '
                'currently stand. The PDF is rendered in the same dark theme; '
                'generating it takes a few seconds because every chart is redrawn '
                'at print resolution.</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate PDF"):
            with st.spinner("Rendering charts and building the PDF..."):
                resolved = []
                for kind, content in doc.blocks:
                    if kind == "img":
                        caption, getter = content
                        resolved.append(("img", (caption, getter())))
                    else:
                        resolved.append((kind, content))
                st.session_state["report_pdf"] = build_pdf(resolved, source, len(df))
            st.success("PDF ready — the download button is now active.")

        if "report_pdf" in st.session_state:
            st.download_button(
                label="Download report (PDF)",
                data=st.session_state["report_pdf"],
                file_name="movieiq_project_report.pdf",
                mime="application/pdf",
            )

    with col2:
        st.download_button(
            label="Download report (Markdown)",
            data=_to_markdown(doc.blocks).encode("utf-8"),
            file_name="movieiq_project_report.md",
            mime="text/markdown",
        )