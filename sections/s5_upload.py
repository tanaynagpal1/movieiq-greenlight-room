"""Section — Upload Data.
Shows which dataset is active, offers it for download, and lets the user
run the entire dashboard on their own CSV instead of the bundled movies.csv.
Everything downstream (cleaning, audit, EDA, model, statistics, simulation,
conclusions) recomputes automatically.
"""
import streamlit as st
from src.loader import (
    load_raw_from_bytes,
    validate_columns,
    REQUIRED_COLUMNS,
)


def render(df):
    st.markdown('<div class="hero-title" style="font-size:1.6rem">Upload Data</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">'
        'By default this dashboard runs on the bundled movies.csv. Upload your '
        'own CSV here and every section — the audit, charts, statistical tests, '
        'model and risk simulator — recalculates on your data instead.'
        '</div>',
        unsafe_allow_html=True,
    )

    using_custom = "file_bytes" in st.session_state
    source_name = st.session_state.get("file_name", "uploaded file")

    st.markdown(
        '<div class="panel">'
        '<div class="panel-title">Active Dataset</div>'
        '<div style="color:#EDE9F5;font-size:.9rem;margin-bottom:.7rem">'
        + (
            f'Currently using your uploaded file: '
            f'<span style="font-family:\'JetBrains Mono\',monospace;color:#2BD9C4">'
            f'{source_name}</span>'
            if using_custom else
            'Currently using the bundled '
            '<span style="font-family:\'JetBrains Mono\',monospace;color:#C9A227">'
            'movies.csv</span>.'
        )
        + '</div>'
        f'<div style="color:#9089AB;font-size:.84rem">'
        f'{len(df):,} rows, cleaned and analysis-ready — includes the derived '
        f'<code>genre</code>, <code>success</code>, <code>roi</code> and '
        f'<code>profit</code> columns.</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.download_button(
        label="Download cleaned dataset (CSV)",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="movieiq_cleaned_data.csv",
        mime="text/csv",
    )

    st.write("")

    st.markdown(
        '<div class="panel"><div class="panel-title">Required Columns</div>'
        '<div style="color:#9089AB;font-size:.86rem;line-height:1.9">'
        'Your CSV must contain these seven columns. Anything else is ignored.<br>'
        '<span style="font-family:\'JetBrains Mono\',monospace;color:#C9A227">'
        + " · ".join(REQUIRED_COLUMNS) +
        '</span><br><br>'
        'The <code>genres</code> column should hold a stringified list, e.g. '
        '<code>[{\'id\': 18, \'name\': \'Drama\'}]</code>. Empty lists are '
        'relabelled "Unspecified" rather than dropped.'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.write("")

    uploaded = st.file_uploader("Upload your movies CSV file", type="csv")

    if uploaded is not None:
        file_bytes = uploaded.getvalue()

        try:
            raw = load_raw_from_bytes(file_bytes)
        except Exception as exc:
            st.error(f"Could not read that file as a CSV. Details: {exc}")
            return

        missing = validate_columns(raw)
        if missing:
            st.error(
                "That CSV is missing required column(s): "
                + ", ".join(missing)
                + ". Please upload a file containing all seven required columns."
            )
            return

        if len(raw) < 30:
            st.warning(
                f"That file has only {len(raw)} rows. The dashboard will run, "
                "but statistical tests and simulations need more data to be meaningful."
            )

        st.session_state["file_bytes"] = file_bytes
        st.session_state["file_name"] = uploaded.name
        st.success(
            f"Loaded {len(raw):,} rows from {uploaded.name}. "
            "Every section now runs on your data."
        )
        st.rerun()

    if using_custom:
        st.write("")
        if st.button("Revert to bundled movies.csv"):
            del st.session_state["file_bytes"]
            st.session_state.pop("file_name", None)
            st.rerun()