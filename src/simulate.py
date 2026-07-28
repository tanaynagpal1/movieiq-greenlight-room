"""Monte Carlo risk simulation for MovieIQ — Risk Simulator section.
Draws revenue multipliers (revenue / budget) empirically from the actual
data via resampling, rather than assuming a parametric distribution.
This keeps the simulator honest under filtering: if the sidebar filters
change df_view, the simulator's draws reflect that same filtered slice.
"""
import numpy as np
import pandas as pd

MAX_DRAWS = 20_000  # cap per blueprint's free-tier resource guidance


def get_multipliers(df: pd.DataFrame) -> np.ndarray:
    """The empirical revenue/budget multiplier for every film in view."""
    return (df["revenue"] / df["budget"]).to_numpy()


def simulate_breakeven(df: pd.DataFrame, budget: float,
                        n_draws: int = MAX_DRAWS, seed: int = 42):
    """Monte Carlo break-even simulation for a single film of the given budget.
    Draws n_draws revenue multipliers (with replacement) from the empirical
    distribution and returns the resulting profit distribution and summary stats.
    """
    n_draws = min(n_draws, MAX_DRAWS)
    rng = np.random.default_rng(seed)
    multipliers = get_multipliers(df)

    draws = rng.choice(multipliers, size=n_draws, replace=True)
    revenues = budget * draws
    profits = revenues - budget

    percentiles = {p: float(np.percentile(profits, p)) for p in (5, 25, 50, 75, 95)}

    return {
        "budget": budget,
        "n_draws": n_draws,
        "profits": profits,
        "p_profit": float((profits > 0).mean()),
        "expected_profit": float(profits.mean()),
        "var_5": percentiles[5],
        "percentiles": percentiles,
    }


def simulate_slate_roi(df: pd.DataFrame, slate_size: int,
                        n_portfolios: int = MAX_DRAWS, seed: int = 42) -> np.ndarray:
    """Simulates n_portfolios slates, each of slate_size films with equal budgets.
    Since budgets are equal, portfolio ROI = mean(multipliers) - 1.
    Returns an array of portfolio ROI outcomes.
    """
    n_portfolios = min(n_portfolios, MAX_DRAWS)
    rng = np.random.default_rng(seed)
    multipliers = get_multipliers(df)

    draws = rng.choice(multipliers, size=(n_portfolios, slate_size), replace=True)
    portfolio_roi = draws.mean(axis=1) - 1
    return portfolio_roi