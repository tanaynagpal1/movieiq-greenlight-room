"""Section — Ask AI.
Rule-based, grounded entirely in this dataset's computed facts — no
external API, no key, no training. Matches keywords in the question to
the same numbers the Report section narrates, and answers from them.
"""
import streamlit as st

from src.rule_ai import answer

SUGGESTED_QUESTIONS = [
    "What's the model's verdict, and why?",
    "Which genre performs best right now?",
    "What's the risk on a $50M film?",
    "Explain the statistical test results",
]


def _ask(df, raw_df, question):
    st.session_state["ai_history"].append({"role": "user", "text": question})
    reply = answer(df, raw_df, question)
    st.session_state["ai_history"].append({"role": "model", "text": reply})


def render(df, raw_df):
    st.markdown('<div class="hero-title" style="font-size:1.6rem">Ask AI</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="section-sub">'
        'Ask about the model, genres, risk, statistics, or data quality on the '
        'dataset currently loaded. Every answer is built from this app\'s own '
        'computed numbers — nothing is generated or invented, and no external '
        'AI service is used.'
        '</div>',
        unsafe_allow_html=True,
    )

    if "ai_history" not in st.session_state:
        st.session_state["ai_history"] = []

    # ---- Empty state: greeting + suggested question chips ----
    if not st.session_state["ai_history"]:
        st.markdown(
            '<div style="padding:.4rem 0 .6rem">'
            '<div style="font-family:\'Rajdhani\',sans-serif;font-size:1.4rem;'
            'font-weight:700;color:#fff">Hello 👋</div>'
            '<div style="color:#9089AB;font-size:.92rem;margin-top:.2rem">'
            'How can I help with this dataset today?</div></div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        for i, q in enumerate(SUGGESTED_QUESTIONS):
            with cols[i % 2]:
                if st.button(q, key=f"suggest_{i}", use_container_width=True):
                    _ask(df, raw_df, q)
                    st.rerun()
        st.write("")

    # ---- Chat history ----
    for turn in st.session_state["ai_history"]:
        with st.chat_message("user" if turn["role"] == "user" else "assistant"):
            st.markdown(turn["text"].replace("$", "\\$"))

    # ---- Input box ----
    question = st.chat_input("Ask about the current dataset...")
    if question:
        with st.chat_message("user"):
            st.markdown(question)
        with st.chat_message("assistant"):
            with st.spinner("Looking it up..."):
                _ask(df, raw_df, question)
                reply = st.session_state["ai_history"][-1]["text"]
            st.markdown(reply.replace("$", "\\$"))

    if st.session_state["ai_history"]:
        st.write("")
        if st.button("Clear conversation"):
            st.session_state["ai_history"] = []
            st.rerun()