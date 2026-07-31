"""Rule-based Ask AI. No external API, no training, no key required.
Matches keywords in the question to the same computed facts the Report
section uses, and returns a plain-language answer built from them.
Honest limitation: this understands topics, not open-ended phrasing —
it's a grounded FAQ engine over real numbers, not a language model.
"""
import re

from src.audit import run_checks, health_score
from src.stats_lab import run_ttest, run_chi_square, ALPHA_DEFAULT
from src.model import train_model
from src.simulate import simulate_breakeven, simulate_slate_roi

GREETINGS = {"hi", "hello", "hey", "yo", "hiya", "sup"}

TOPICS = {
    "model":    ["model", "predict", "prediction", "accuracy", "signal",
                 "random forest", "auc", "classifier", "forecast"],
    "genre":    ["genre", "genres", "category of film", "type of movie"],
    "risk":     ["risk", "budget", "$", "lose", "loss", "profit", "var",
                 "value at risk", "breakeven", "break-even", "invest"],
    "slate":    ["slate", "portfolio", "diversif", "multiple films",
                 "many films"],
    "stats":    ["significant", "p-value", "p value", "t-test", "ttest",
                 "chi-square", "chi square", "hypothesis", "statistic"],
    "quality":  ["clean", "audit", "missing", "health score", "data quality",
                 "duplicate", "outlier"],
    "roi":      ["correlat", "return", "roi", "bigger budget", "spend more"],
    "profile":  ["how many", "rows", "size of the dataset", "how much data",
                 "dataset size"],
}

_BUDGET_RE = re.compile(
    r"\$?\s*(\d+(?:\.\d+)?)\s*(m|mn|million)\b", re.IGNORECASE
)
_SLATE_RE = re.compile(
    r"(\d+)\s*[- ]?\s*(film|movie|title)s?\b", re.IGNORECASE
)


def _matches(question, keywords):
    q = question.lower()
    return any(k in q for k in keywords)


def _extract_budget(question, default_m):
    m = _BUDGET_RE.search(question)
    if m:
        return float(m.group(1))
    return default_m


def _extract_slate_size(question, default_n=20):
    m = _SLATE_RE.search(question)
    if m:
        n = int(m.group(1))
        return max(1, min(n, 30))
    return default_n


def _answer_model(df):
    if df["success"].nunique() < 2:
        return ("The active dataset has only one outcome class, so no model "
                "could be trained.")
    if len(df) < 50:
        return f"Only {len(df)} rows are in view — too few to train a reliable model."
    results = train_model(df)
    label, _tone, _expl = results["verdict"]
    lift = results["acc_model"] - results["acc_baseline"]
    top_feat = max(results["importances"], key=results["importances"].get)
    base = (f"The Random Forest scores {results['acc_model']*100:.1f}% accuracy "
            f"against a baseline of {results['acc_baseline']*100:.1f}% (always "
            f"predicting the majority class) — a lift of {lift*100:+.1f} points. "
            f"ROC-AUC is {results['auc']:.3f}, where 0.500 is a coin flip.")
    if label == "NO SIGNAL":
        tail = (" Verdict: NO SIGNAL. The model carries no usable information — "
                "any accuracy shown is the base rate in disguise. This is a "
                "finding about the available features, not a failure of the "
                "algorithm.")
    elif label == "MARGINAL":
        tail = (f" Verdict: MARGINAL. There's a small edge over guessing, likely "
                f"within noise. `{top_feat}` was the most informative feature.")
    else:
        tail = (f" Verdict: PREDICTIVE. The features carry genuine signal. "
                f"`{top_feat}` was the most informative feature.")
    return base + tail


def _answer_genre(df):
    rates = df.groupby("genre")["success"].agg(["mean", "count"])
    rates = rates[rates["count"] >= 10].sort_values("mean")
    if len(rates) < 2:
        return "Not enough genres with sufficient sample size in the current view to compare."
    spread = (rates["mean"].iloc[-1] - rates["mean"].iloc[0]) * 100
    best, worst = rates.index[-1], rates.index[0]
    verdict = ("That's a narrow spread — consistent with genre carrying little "
               "real signal." if spread < 10 else
               "That's a wide enough spread to be worth investigating further.")
    return (f"{best} has the highest success rate "
            f"({rates['mean'].iloc[-1]*100:.1f}%); {worst} has the lowest "
            f"({rates['mean'].iloc[0]*100:.1f}%) — a spread of {spread:.1f} "
            f"percentage points. {verdict}")


def _answer_risk(df, question):
    if len(df) < 30:
        return "Too few films in the current view to simulate risk reliably."
    default_m = min(max(df["budget"].median() / 1e6, 1), 250)
    budget_m = _extract_budget(question, default_m)
    sim = simulate_breakeven(df, budget_m * 1_000_000, seed=42)
    return (f"At a ${budget_m:.0f}M budget, simulated from {sim['n_draws']:,} "
            f"draws on films currently in view: {sim['p_profit']*100:.1f}% chance "
            f"of profit, expected outcome ${sim['expected_profit']/1e6:+.1f}M, "
            f"and a 5% value-at-risk of ${sim['var_5']/1e6:+.1f}M — meaning a "
            f"one-in-twenty chance of losing at least that much.")


def _answer_slate(df, question):
    if len(df) < 30:
        return "Too few films in the current view to simulate a slate reliably."
    size = _extract_slate_size(question)
    roi = simulate_slate_roi(df, size, seed=42)
    p_profit = float((roi > 0).mean())
    roi1 = simulate_slate_roi(df, 1, seed=42)
    p1 = float((roi1 > 0).mean())
    return (f"A {size}-film slate is profitable in {p_profit*100:.1f}% of "
            f"simulations, versus {p1*100:.1f}% for a single film. "
            f"Diversification doesn't change the odds on any one title — it "
            f"narrows the spread of the combined outcome.")


def _answer_stats(df):
    t = run_ttest(df, feature="vote_average")
    c = run_chi_square(df, feature="genre")
    t_sig = t["p_value"] < ALPHA_DEFAULT
    c_sig = c["p_value"] < ALPHA_DEFAULT
    t_word = "significant" if t_sig else "not significant"
    c_word = "significant" if c_sig else "not significant"
    return (f"T-test on vote_average by success: t = {t['t_stat']:.3f}, "
            f"p = {t['p_value']:.4f} — {t_word} at α = {ALPHA_DEFAULT:.2f}. "
            f"Chi-square on genre vs success: χ² = {c['chi2_stat']:.3f}, "
            f"p = {c['p_value']:.4f} — {c_word}. Neither result would survive a "
            f"Bonferroni correction if it were borderline, since two tests were run.")


def _answer_quality(raw_df):
    checks = run_checks(raw_df)
    score = health_score(checks)
    n_pass = sum(1 for c in checks if c["verdict"] == "pass")
    n_flag = sum(1 for c in checks if c["verdict"] == "flag")
    n_crit = sum(1 for c in checks if c["verdict"] == "critical")
    return (f"Data health score: {score}/100 across 12 checks "
            f"({n_pass} passed, {n_flag} flagged, {n_crit} critical). See the "
            f"Data Quality section for the full ledger and reasoning behind "
            f"each check.")


def _answer_roi(df):
    corr_br = df["budget"].corr(df["revenue"])
    corr_broi = df["budget"].corr(df["roi"])
    return (f"Budget correlates with raw revenue at r = {corr_br:+.2f}, which "
            f"looks strong but is mostly structural — bigger films have bigger "
            f"numbers on both sides. The more relevant figure is budget versus "
            f"ROI: r = {corr_broi:+.3f}"
            + (", essentially zero. Spending more doesn't buy a better return."
               if abs(corr_broi) < 0.10 else
               ", worth a closer look — spend does relate to return here."))


def _answer_profile(df):
    return (f"{len(df):,} films are currently in view, across "
            f"{df['genre'].nunique()} genres, with a "
            f"{df['success'].mean()*100:.1f}% success rate and a median ROI of "
            f"{df['roi'].median()*100:+.1f}%.")


def answer(df, raw_df, question):
    """Returns a plain-language answer built from computed facts, or a
    fallback listing what it can talk about."""
    q = question.strip().lower()

    if q in GREETINGS or (len(q) <= 6 and _matches(q, GREETINGS)):
        return ("Hello! Ask me about the model's accuracy, genre performance, "
                "risk on a given budget, the statistical tests, data quality, "
                "or the ROI relationship — I'll answer from the numbers "
                "currently computed on this dataset.")

    parts = []
    if _matches(q, TOPICS["slate"]):
        parts.append(_answer_slate(df, question))
    elif _matches(q, TOPICS["risk"]):
        parts.append(_answer_risk(df, question))
    if _matches(q, TOPICS["model"]):
        parts.append(_answer_model(df))
    if _matches(q, TOPICS["genre"]):
        parts.append(_answer_genre(df))
    if _matches(q, TOPICS["stats"]):
        parts.append(_answer_stats(df))
    if _matches(q, TOPICS["quality"]):
        parts.append(_answer_quality(raw_df))
    if _matches(q, TOPICS["roi"]):
        parts.append(_answer_roi(df))
    if _matches(q, TOPICS["profile"]):
        parts.append(_answer_profile(df))

    if parts:
        return "\n\n".join(parts)

    return (
        "I can only answer questions about what's actually computed on this "
        "dataset — I'm not a general-purpose AI, just a lookup over the app's "
        "own numbers. Try asking about:\n\n"
        "- the **model** (accuracy, verdict, prediction)\n"
        "- **genre** performance\n"
        "- **risk** at a given budget, e.g. \"what's the risk on a $50M film\"\n"
        "- a **slate**, e.g. \"how does a 10-film slate compare\"\n"
        "- the **statistical tests** (t-test, chi-square, significance)\n"
        "- **data quality** (the audit, health score)\n"
        "- **budget and ROI** correlation\n"
        "- the **dataset** (row count, genres, success rate)"
    )