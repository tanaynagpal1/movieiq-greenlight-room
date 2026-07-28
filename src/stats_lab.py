"""Statistical testing logic for MovieIQ — Brief Stage 3.
Pure functions only: no Streamlit code in this file.
Every function returns plain Python/NumPy values so the rendering
layer (sections/s2_statistical_tests.py) can format them freely.
"""
import numpy as np
import pandas as pd
from scipy import stats

ALPHA_DEFAULT = 0.05


def run_ttest(df: pd.DataFrame, feature: str = "vote_average"):
    """Independent-samples t-test comparing `feature` between
    successful (success == 1) and unsuccessful (success == 0) films.

    Returns a dict:
        feature, group0_mean, group1_mean, group0_n, group1_n,
        t_stat, p_value
    """
    group0 = df.loc[df["success"] == 0, feature].dropna()
    group1 = df.loc[df["success"] == 1, feature].dropna()

    t_stat, p_value = stats.ttest_ind(group1, group0, equal_var=False)

    return {
        "feature": feature,
        "group0_mean": float(group0.mean()),
        "group1_mean": float(group1.mean()),
        "group0_n": int(group0.shape[0]),
        "group1_n": int(group1.shape[0]),
        "t_stat": float(t_stat),
        "p_value": float(p_value),
    }


def run_chi_square(df: pd.DataFrame, feature: str = "genre"):
    """Chi-square test of independence between `feature` (categorical)
    and success.

    Returns a dict:
        feature, chi2_stat, p_value, dof, contingency_table (DataFrame)
    """
    contingency = pd.crosstab(df[feature], df["success"])
    chi2_stat, p_value, dof, _expected = stats.chi2_contingency(contingency)

    return {
        "feature": feature,
        "chi2_stat": float(chi2_stat),
        "p_value": float(p_value),
        "dof": int(dof),
        "contingency_table": contingency,
    }


def bonferroni_alpha(alpha: float, n_tests: int) -> float:
    """Family-wise corrected significance threshold."""
    return alpha / n_tests


def verdict(p_value: float, alpha: float = ALPHA_DEFAULT) -> str:
    """Plain-language significance call at the given alpha."""
    return "SIGNIFICANT" if p_value < alpha else "NOT SIGNIFICANT"


def permutation_test(df: pd.DataFrame, feature: str = "vote_average",
                      n_permutations: int = 2000, seed: int = 42):
    """Empirical null distribution for the mean-difference statistic
    on `feature` between success groups, built by shuffling the
    success labels n_permutations times.

    Returns a dict:
        observed_diff, null_diffs (np.ndarray), empirical_p_value
    """
    rng = np.random.default_rng(seed)

    values = df[feature].dropna().to_numpy()
    labels = df.loc[df[feature].notna(), "success"].to_numpy()

    observed_diff = values[labels == 1].mean() - values[labels == 0].mean()

    null_diffs = np.empty(n_permutations)
    shuffled = labels.copy()
    for i in range(n_permutations):
        rng.shuffle(shuffled)
        null_diffs[i] = values[shuffled == 1].mean() - values[shuffled == 0].mean()

    empirical_p = float(np.mean(np.abs(null_diffs) >= np.abs(observed_diff)))

    return {
        "feature": feature,
        "observed_diff": float(observed_diff),
        "null_diffs": null_diffs,
        "empirical_p_value": empirical_p,
        "n_permutations": n_permutations,
    }