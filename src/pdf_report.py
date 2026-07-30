"""PDF builder for the MovieIQ project report.
Consumes the same block list the on-screen report is built from, so the PDF
and the app can never drift apart. Uses fpdf2 (pure Python, no system
dependencies) and core fonts, so it deploys cleanly on Streamlit Cloud.
"""
import re

from fpdf import FPDF

INK = (11, 9, 16)
SURF = (23, 17, 35)
BORDER = (42, 32, 56)
GOLD = (201, 162, 39)
PURPLE = (157, 92, 255)
TEAL = (43, 217, 196)
RED = (224, 82, 107)
TEXT = (237, 233, 245)
DIM = (144, 137, 171)
FAINT = (92, 84, 115)

PAGE_W, PAGE_H = 210, 297
MARGIN = 16
CONTENT_W = PAGE_W - 2 * MARGIN

_REPLACEMENTS = {
    "\u2014": " - ", "\u2013": "-", "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u00d7": "x",
    "\u03b1": "alpha", "\u03c7\u00b2": "chi-squared", "\u03c7": "chi",
    "\u00b1": "+/-", "\u2248": "~", "\u00b2": "2", "\u2192": "->",
    "\u00b7": "-", "\u2265": ">=", "\u2264": "<=", "\u00b0": "deg",
}


def _clean(text):
    """Strip markdown markers and reduce to latin-1-safe characters."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"\1", text)
    for src, dst in _REPLACEMENTS.items():
        text = text.replace(src, dst)
    return text.encode("latin-1", "replace").decode("latin-1")


class _Report(FPDF):
    def header(self):
        self.set_fill_color(*INK)
        self.rect(0, 0, PAGE_W, PAGE_H, style="F")

    def footer(self):
        self.set_y(-12)
        self.set_font("helvetica", "", 7)
        self.set_text_color(*FAINT)
        self.cell(0, 5, f"Movie Revenue Analysis  |  page {self.page_no()}",
                  align="C")


def _room(pdf, needed):
    """Start a new page if less than `needed` mm remains."""
    if pdf.get_y() + needed > PAGE_H - 20:
        pdf.add_page()


def build_pdf(blocks, source_label, row_count):
    pdf = _Report(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.add_page()

    # ---- cover block ----
    pdf.set_y(34)
    pdf.set_font("helvetica", "", 8)
    pdf.set_text_color(*GOLD)
    pdf.cell(0, 5, "PROJECT REPORT", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("helvetica", "B", 26)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 12, "Movie Revenue Analysis", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(*DIM)
    pdf.multi_cell(CONTENT_W, 5.5, _clean(
        "A risk-intelligence report on film investment. The business framing is "
        "fixed; every figure below was computed from the dataset named underneath."))
    pdf.ln(3)
    pdf.set_draw_color(*GOLD)
    pdf.set_line_width(0.6)
    pdf.line(MARGIN, pdf.get_y(), MARGIN + 34, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("helvetica", "", 8.5)
    pdf.set_text_color(*FAINT)
    pdf.cell(0, 5, _clean(f"Source: {source_label}  |  {row_count:,} rows"),
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    for kind, content in blocks:
        if kind == "h2":
            _room(pdf, 26)
            pdf.ln(3)
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(*GOLD)
            pdf.multi_cell(CONTENT_W, 7, _clean(content))
            pdf.set_draw_color(*BORDER)
            pdf.set_line_width(0.3)
            pdf.line(MARGIN, pdf.get_y() + 1, PAGE_W - MARGIN, pdf.get_y() + 1)
            pdf.ln(4)

        elif kind == "h3":
            _room(pdf, 18)
            pdf.ln(1)
            pdf.set_font("helvetica", "B", 10.5)
            pdf.set_text_color(255, 255, 255)
            pdf.multi_cell(CONTENT_W, 5.5, _clean(content))
            pdf.ln(1.5)

        elif kind == "p":
            _room(pdf, 16)
            pdf.set_font("helvetica", "", 9.5)
            pdf.set_text_color(*TEXT)
            pdf.multi_cell(CONTENT_W, 5, _clean(content))
            pdf.ln(2.5)

        elif kind == "ul":
            for item in content:
                _room(pdf, 14)
                y0 = pdf.get_y()
                pdf.set_font("helvetica", "B", 9.5)
                pdf.set_text_color(*GOLD)
                pdf.set_xy(MARGIN, y0)
                pdf.cell(4, 5, "-")
                pdf.set_font("helvetica", "", 9.5)
                pdf.set_text_color(*TEXT)
                pdf.set_xy(MARGIN + 4.5, y0)
                pdf.multi_cell(CONTENT_W - 4.5, 5, _clean(item))
                pdf.ln(1.2)
            pdf.ln(1.5)

        elif kind == "kpis":
            _room(pdf, 24)
            n = len(content)
            gap = 3
            w = (CONTENT_W - gap * (n - 1)) / n
            y0 = pdf.get_y()
            for i, (label, value) in enumerate(content):
                x = MARGIN + i * (w + gap)
                pdf.set_fill_color(*SURF)
                pdf.set_draw_color(*BORDER)
                pdf.set_line_width(0.25)
                pdf.rect(x, y0, w, 17, style="DF")
                pdf.set_xy(x + 2.5, y0 + 2.4)
                pdf.set_font("helvetica", "", 6.4)
                pdf.set_text_color(*FAINT)
                pdf.cell(w - 5, 3.4, _clean(label.upper()))
                pdf.set_xy(x + 2.5, y0 + 7.4)
                pdf.set_font("helvetica", "B", 13)
                pdf.set_text_color(255, 255, 255)
                pdf.cell(w - 5, 7, _clean(str(value)))
            pdf.set_y(y0 + 17)
            pdf.ln(4)

        elif kind == "img":
            caption, png = content
            png.seek(0)
            _room(pdf, 95)
            pdf.image(png, x=MARGIN, w=CONTENT_W)
            pdf.ln(1.5)
            pdf.set_font("helvetica", "I", 8)
            pdf.set_text_color(*DIM)
            pdf.multi_cell(CONTENT_W, 4.2, _clean(caption))
            pdf.ln(4)

    return bytes(pdf.output())