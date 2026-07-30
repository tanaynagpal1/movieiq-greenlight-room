"""Data loading and cleaning for MovieIQ.
Supports two sources:
  - the bundled data/movies.csv (the default the app opens with)
  - a CSV uploaded by the user via the Upload Data section
Both run through the same cleaning logic, so every section behaves
identically whichever source is active.
"""
import ast
import io
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_PATH = Path(__file__).parent.parent / "data" / "movies.csv"

REQUIRED_COLUMNS = [
    "budget", "revenue", "popularity", "runtime",
    "vote_average", "title", "genres",
]


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


def validate_columns(df):
    """Returns a list of required columns missing from the given dataframe."""
    return [c for c in REQUIRED_COLUMNS if c not in df.columns]


def clean_dataframe(raw):
    """The shared cleaning pipeline. Applied to whichever source is active."""
    df = raw.copy()

    # --- Genre: parse the stringified list, take the first genre, ---
    # --- relabel empty "[]" rows as "Unspecified" rather than dropping them. ---
    df["genre"] = df["genres"].apply(_parse_genre)

    # --- vote_average may arrive at ~15 decimal places, a synthetic-data artefact. ---
    # --- Round for display; keep the original full-precision column for modelling. ---
    df["vote_average_display"] = df["vote_average"].round(1)

    # --- Target and derived metrics. revenue itself is never fed to the model — ---
    # --- it's what defines success, so including it would be target leakage. ---
    df["success"] = (df["revenue"] > df["budget"]).astype(int)
    df["roi"] = (df["revenue"] - df["budget"]) / df["budget"]
    df["profit"] = df["revenue"] - df["budget"]

    return df


# ---------------- Default source: bundled movies.csv ----------------

@st.cache_data
def load_raw():
    """The bundled file, untouched. Used by audit.py for before/after comparison."""
    return pd.read_csv(DATA_PATH)


@st.cache_data
def load_clean():
    """The bundled file, cleaned and analysis-ready."""
    return clean_dataframe(pd.read_csv(DATA_PATH))


# ---------------- Uploaded source ----------------

@st.cache_data
def load_raw_from_bytes(file_bytes):
    """An uploaded CSV, untouched."""
    return pd.read_csv(io.BytesIO(file_bytes))


@st.cache_data
def load_clean_from_bytes(file_bytes):
    """An uploaded CSV, cleaned and analysis-ready."""
    return clean_dataframe(pd.read_csv(io.BytesIO(file_bytes)))