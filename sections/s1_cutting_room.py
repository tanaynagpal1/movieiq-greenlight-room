"""Section 01 — The Cutting Room."""
import streamlit as st
from src.audit import render_audit_panel


def render():
    st.markdown('<div class="hero-title" style="font-size:1.6rem">The Cutting Room</div>',
                unsafe_allow_html=True)
    render_audit_panel()