"""Placeholder for sections not yet built."""
import streamlit as st


def render(title):
    st.markdown(f'<div class="hero-title" style="font-size:1.6rem">{title}</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div style="color:#5C5473;font-size:.9rem;margin-top:1rem">'
        'This section is next on the build order.</div>',
        unsafe_allow_html=True,
    )