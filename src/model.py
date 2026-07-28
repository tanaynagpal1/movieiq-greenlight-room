"""Random Forest model for MovieIQ — Prediction Model section.
Trained on budget, popularity, runtime, vote_average only.
revenue is excluded: it defines the target, so including it is leakage."""
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix

FEATURES = ["budget", "popularity", "runtime", "vote_average"]


@st.cache_resource
def train_model(df):
    """Trains once, cached across reruns. Returns everything the
    Prediction Model section and the predictor sliders need."""
    X = df[FEATURES]
    y = df["success"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    acc_model = accuracy_score(y_test, y_pred)
    acc_baseline = y_test.mean()  # always predicting "success"
    auc = roc_auc_score(y_test, y_proba)

    cv = cross_val_score(
        model, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=1),
        scoring="roc_auc",
    )

    cm = confusion_matrix(y_test, y_pred)

    importances = dict(zip(FEATURES, model.feature_importances_))

    lift = acc_model - acc_baseline
    if auc < 0.55 and lift <= 0:
        verdict = ("NO SIGNAL", "red",
                    "The features carry no information about success. "
                    "Any accuracy shown is the base rate in disguise.")
    elif lift < 0.02:
        verdict = ("MARGINAL", "gold",
                    "A small edge over guessing, likely within noise.")
    else:
        verdict = ("PREDICTIVE", "teal",
                    "The model beats the baseline by a meaningful margin.")

    return {
        "model": model,
        "acc_model": acc_model,
        "acc_baseline": acc_baseline,
        "auc": auc,
        "cv_auc_mean": cv.mean(),
        "cv_auc_std": cv.std(),
        "confusion_matrix": cm,
        "importances": importances,
        "verdict": verdict,
        "X_test": X_test,
        "y_test": y_test,
        "y_proba": y_proba,
    }


def predict_one(model, budget, popularity, runtime, vote_average):
    """Used by the predictor sliders. Returns probability of success."""
    X = pd.DataFrame(
        [[budget, popularity, runtime, vote_average]], columns=FEATURES
    )
    return model.predict_proba(X)[0][1]