"""Data loading and cleaning for MovieIQ — Section 01: The Cutting Room."""
import ast
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent.parent / "data" / "movies.csv"


def _parse_genre(raw):
    """Genres arrive as a stringified Python list, e.g. "[{'id': 10749, 'name': 'Romance'}]".
    ast.literal_eval handles the single quotes safely; json.loads would fail on them."""
    try:
        parsed = ast.literal_eval(raw)
        if isinstance(parsed, list) and len(parsed) > 0:
            return parsed[0]["name"]
    except (ValueError, SyntaxError, TypeError, KeyError):
        pass
    return "Unspecified"


@st.cache_data
def load_raw():
    """The untouched file, exactly as it sits on disk. Used only by audit.py
    to compare before/after — never used for analysis."""
    return pd.read_csv(DATA_PATH)


@st.cache_data
def load_clean():
    """The cleaned, analysis-ready dataframe every section should import."""
    df = pd.read_csv(DATA_PATH)

    # --- Genre: parse the stringified list, take the first genre, ---
    # --- relabel the 181 empty "[]" rows as "Unspecified" rather than dropping them. ---
    # --- Their success rate (81.2%) matches the labelled rows (80.7%) — missing at ---
    # --- random, so dropping them would only throw away 9% of the file for nothing. ---
    df["genre"] = df["genres"].apply(_parse_genre)

    # --- vote_average arrives at ~15 decimal places, a synthetic-data artefact. ---
    # --- Round for display; keep the original full-precision column for modelling. ---
    df["vote_average_display"] = df["vote_average"].round(1)

    # --- Target and derived metric. revenue itself is never fed to the model — ---
    # --- it's what defines success, so including it would be target leakage. ---
    df["success"] = (df["revenue"] > df["budget"]).astype(int)
    df["roi"] = (df["revenue"] - df["budget"]) / df["budget"]
    df["profit"] = df["revenue"] - df["budget"]

    return df