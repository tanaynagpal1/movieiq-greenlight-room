"""Design system for MovieIQ — The Greenlight Room."""
import streamlit as st

# ── Palette ────────────────────────────────────────────────
INK    = "#0B0E14"   # screening black — base
SURF   = "#141A24"   # reel grey — surface
BORD   = "#2A3441"   # edge
GOLD   = "#F2B33D"   # marquee gold — break-even, user controls
TEAL   = "#35C2C9"   # projector teal — observed data
GREEN  = "#3DD68C"   # green light — profit
RED    = "#FF5C66"   # red carpet — loss
VIOLET = "#A78BFA"   # matinee violet — simulated
ASH    = "#96A2B4"   # body text
WHITE  = "#F2F4F8"   # headings

# NOTE: no blank lines allowed inside this string — a blank line ends the
# HTML block in markdown and the rest of the CSS renders as visible text.
_CSS = """<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
.stApp { background:#0B0E14; }
.block-container { padding-top:2.2rem; padding-bottom:3rem; max-width:1500px; }
html, body, [class*="css"] { font-family:'Poppins', sans-serif; }
h1, h2, h3, h4 { font-family:'Poppins', sans-serif; color:#F2F4F8; letter-spacing:-0.02em; }
#MainMenu, footer { visibility:hidden; }
[data-testid="stHeader"] { background:rgba(0,0,0,0); }
[data-testid="stSidebar"] { background:#0E131B; border-right:1px solid #2A3441; }
.hero-kicker { font-size:.70rem; letter-spacing:.3em; text-transform:uppercase; color:#F2B33D; font-weight:600; margin-bottom:.5rem; }
.hero-title { font-size:2.6rem; font-weight:600; line-height:1.05; color:#fff; margin:0 0 .3rem 0; }
.hero-title span { color:#F2B33D; }
.hero-sub { color:#96A2B4; font-size:1rem; font-weight:300; margin:0 0 1.8rem 0; }
.kpi { background:#141A24; border:1px solid #2A3441; border-left:3px solid #35C2C9; border-radius:10px; padding:1rem 1.1rem; height:100%; }
.kpi.gold { border-left-color:#F2B33D; }
.kpi.green { border-left-color:#3DD68C; }
.kpi.red { border-left-color:#FF5C66; }
.kpi-label { font-size:.64rem; letter-spacing:.14em; text-transform:uppercase; color:#5C6879; font-weight:500; }
.kpi-value { font-family:'JetBrains Mono',monospace; font-size:1.85rem; font-weight:600; color:#35C2C9; line-height:1.15; margin-top:.35rem; }
.kpi.gold .kpi-value { color:#F2B33D; }
.kpi.green .kpi-value { color:#3DD68C; }
.kpi.red .kpi-value { color:#FF5C66; }
.kpi-delta { font-size:.72rem; color:#5C6879; margin-top:.3rem; }
</style>"""


def inject_css():
    """Call once, immediately after st.set_page_config()."""
    st.markdown(_CSS, unsafe_allow_html=True)


def kpi_card(label, value, delta="", tone="teal"):
    """Replaces st.metric. tone: teal | gold | green | red"""
    st.markdown(
        f'<div class="kpi {tone}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-delta">{delta}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )