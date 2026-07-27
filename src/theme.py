"""Design system for MovieIQ — The Greenlight Room (console theme)."""
import streamlit as st

INK    = "#07060B"
SURF   = "#100C19"
SURF2  = "#171123"
BORD   = "#2A2038"
GOLD   = "#C9A227"
PURPLE = "#9D5CFF"
TEAL   = "#2BD9C4"
RED    = "#E0526B"
TEXT   = "#EDE9F5"
DIM    = "#9089AB"
FAINT  = "#5C5473"

_CSS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@600;700&family=Inter:wght@400;500&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
<style>
.stApp { background:#07060B; background-image:radial-gradient(circle at 15% 10%, rgba(108,43,217,0.10), transparent 40%), radial-gradient(circle at 90% 80%, rgba(43,217,196,0.06), transparent 45%); }
.stApp::before { content:''; position:fixed; inset:0; z-index:0; opacity:.05; pointer-events:none; background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='56' height='100' viewBox='0 0 56 100'%3E%3Cpath d='M28 0 L56 16 L56 50 L28 66 L0 50 L0 16 Z' fill='none' stroke='%239d5cff' stroke-width='1'/%3E%3C/svg%3E"); background-size:56px 100px; }
.block-container { padding-top:2.2rem; padding-bottom:3rem; max-width:1500px; position:relative; z-index:1; }
html, body, [class*="css"] { font-family:'Inter', sans-serif; color:#EDE9F5; }
h1, h2, h3, h4 { font-family:'Rajdhani', sans-serif; font-weight:700; letter-spacing:.03em; color:#fff; }
#MainMenu, footer { visibility:hidden; }
[data-testid="stHeader"] { background:rgba(0,0,0,0); }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#100C19,#0b0812 90%); border-right:1px solid #2A2038; }
.hero-kicker { font-family:'JetBrains Mono',monospace; font-size:.68rem; letter-spacing:.3em; text-transform:uppercase; color:#C9A227; font-weight:600; margin-bottom:.6rem; }
.hero-title { font-family:'Rajdhani',sans-serif; font-size:2.7rem; font-weight:700; line-height:1.05; color:#fff; letter-spacing:.01em; margin:0 0 .3rem 0; }
.hero-title span { color:#C9A227; }
.hero-sub { color:#9089AB; font-size:1rem; font-weight:400; margin:0 0 1.8rem 0; }
.kpi { background:linear-gradient(160deg,#171123,#100C19); border:1px solid #2A2038; border-radius:8px; padding:1.1rem 1.25rem; height:100%; position:relative; overflow:hidden; }
.kpi::before { content:''; position:absolute; top:-40%; right:-30%; width:120px; height:120px; background:radial-gradient(circle, rgba(157,92,255,0.18), transparent 70%); }
.kpi.gold::before { background:radial-gradient(circle, rgba(201,162,39,0.20), transparent 70%); }
.kpi.teal::before { background:radial-gradient(circle, rgba(43,217,196,0.18), transparent 70%); }
.kpi.red::before { background:radial-gradient(circle, rgba(224,82,107,0.18), transparent 70%); }
.kpi-label { font-size:.66rem; letter-spacing:.16em; text-transform:uppercase; color:#5C5473; font-weight:600; position:relative; z-index:1; }
.kpi-value { font-family:'JetBrains Mono',monospace; font-size:1.9rem; font-weight:700; color:#fff; line-height:1.2; margin-top:.4rem; position:relative; z-index:1; }
.kpi-delta { font-size:.74rem; color:#9089AB; margin-top:.4rem; position:relative; z-index:1; }
.kpi-bar { height:3px; width:100%; background:#2A2038; border-radius:2px; margin-top:.8rem; overflow:hidden; position:relative; z-index:1; }
.kpi-bar span { display:block; height:100%; background:linear-gradient(90deg,#6C2BD9,#9D5CFF); }
.kpi.gold .kpi-bar span { background:linear-gradient(90deg,#7d6a2e,#C9A227); }
.kpi.teal .kpi-bar span { background:linear-gradient(90deg,#1a7a6e,#2BD9C4); }
.kpi.red .kpi-bar span { background:linear-gradient(90deg,#8a2f3d,#E0526B); }
</style>"""


def inject_css():
    """Call once, immediately after st.set_page_config()."""
    st.markdown(_CSS, unsafe_allow_html=True)


def kpi_card(label, value, delta="", tone="purple", pct=70):
    """tone: purple | gold | teal | red. pct drives the glow bar width (0-100)."""
    st.markdown(
        f'<div class="kpi {tone}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-delta">{delta}</div>'
        f'<div class="kpi-bar"><span style="width:{pct}%"></span></div>'
        f'</div>',
        unsafe_allow_html=True,
    )