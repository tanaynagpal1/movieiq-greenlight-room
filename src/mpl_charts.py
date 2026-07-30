"""Matplotlib versions of the app's charts, styled to match the dark theme.
Used only for the PDF export — Plotly cannot produce static images without
kaleido, which is too heavy for Streamlit Community Cloud's free tier.
Each function returns PNG bytes ready to embed in the PDF.
"""
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

INK = "#0B0910"
SURF = "#171123"
GOLD = "#C9A227"
PURPLE = "#9D5CFF"
TEAL = "#2BD9C4"
RED = "#E0526B"
TEXT = "#EDE9F5"
DIM = "#9089AB"
GRID = "#2A2038"


def _new_axes(figsize=(8, 4.2)):
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    fig.patch.set_facecolor(INK)
    ax.set_facecolor(INK)
    for spine in ax.spines.values():
        spine.set_color(GRID)
    ax.tick_params(colors=DIM, labelsize=8)
    ax.grid(True, color=GRID, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    return fig, ax


def _to_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", facecolor=fig.get_facecolor(),
                bbox_inches="tight", pad_inches=0.25)
    plt.close(fig)
    buf.seek(0)
    return buf


def breakeven_scatter_png(df):
    fig, ax = _new_axes()
    win = df[df.success == 1]
    loss = df[df.success == 0]
    ax.scatter(win.budget / 1e6, win.revenue / 1e6, s=6, c=TEAL, alpha=0.5,
               linewidths=0, label="Profitable")
    ax.scatter(loss.budget / 1e6, loss.revenue / 1e6, s=6, c=RED, alpha=0.6,
               linewidths=0, label="Loss")
    top = max(df.budget.max(), df.revenue.max()) / 1e6
    ax.plot([0, top], [0, top], color=GOLD, linestyle="--", linewidth=1.6,
            label="Break-even")
    ax.set_xlabel("Budget ($M)", color=DIM, fontsize=9)
    ax.set_ylabel("Revenue ($M)", color=DIM, fontsize=9)
    leg = ax.legend(frameon=False, fontsize=8, loc="upper left")
    for txt in leg.get_texts():
        txt.set_color(DIM)
    return _to_png(fig)


def genre_success_bar_png(df):
    agg = df.groupby("genre")["success"].mean().sort_values()
    fig, ax = _new_axes(figsize=(8, 0.34 * max(len(agg), 4) + 1.2))
    ax.barh(agg.index, agg.values * 100, color=GOLD, height=0.65)
    ax.axvline(df.success.mean() * 100, color=PURPLE, linestyle=":", linewidth=1.4)
    for i, v in enumerate(agg.values * 100):
        ax.text(v + 0.8, i, f"{v:.1f}%", va="center", color=DIM, fontsize=7.5)
    ax.set_xlabel("Success rate (%)", color=DIM, fontsize=9)
    ax.set_xlim(0, min(agg.values.max() * 100 * 1.18, 105))
    ax.grid(axis="y", visible=False)
    return _to_png(fig)


def correlation_heatmap_png(df):
    cols = ["budget", "popularity", "runtime", "vote_average", "success"]
    corr = df[cols].corr().round(2)
    fig, ax = _new_axes(figsize=(6.4, 5.2))
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list(
        "movieiq", [RED, SURF, TEAL])
    im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols)))
    ax.set_yticks(range(len(cols)))
    ax.set_xticklabels(cols, rotation=40, ha="right", color=DIM, fontsize=8)
    ax.set_yticklabels(cols, color=DIM, fontsize=8)
    for i in range(len(cols)):
        for j in range(len(cols)):
            ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center",
                    color=TEXT, fontsize=7.5)
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.ax.tick_params(colors=DIM, labelsize=7)
    cbar.outline.set_edgecolor(GRID)
    ax.grid(False)
    return _to_png(fig)


def profit_distribution_png(profits):
    fig, ax = _new_axes()
    bins = np.linspace(profits.min(), profits.max(), 55)
    ax.hist(profits[profits <= 0] / 1e6, bins=bins / 1e6, color=RED, label="Loss")
    ax.hist(profits[profits > 0] / 1e6, bins=bins / 1e6, color=PURPLE, label="Profit")
    ax.axvline(0, color=GOLD, linestyle="--", linewidth=1.6)
    ax.set_xlabel("Simulated profit ($M)", color=DIM, fontsize=9)
    ax.set_ylabel("Count", color=DIM, fontsize=9)
    leg = ax.legend(frameon=False, fontsize=8)
    for txt in leg.get_texts():
        txt.set_color(DIM)
    return _to_png(fig)


def slate_roi_png(roi_dict):
    fig, ax = _new_axes()
    colors = {1: RED, 5: GOLD, 20: TEAL}
    for size in sorted(roi_dict):
        ax.hist(roi_dict[size], bins=70, density=True, alpha=0.55,
                color=colors.get(size, PURPLE), label=f"{size}-film slate")
    ax.axvline(0, color=TEXT, linestyle="--", linewidth=1.3)
    ax.set_xlabel("Portfolio ROI", color=DIM, fontsize=9)
    ax.set_ylabel("Density", color=DIM, fontsize=9)
    leg = ax.legend(frameon=False, fontsize=8)
    for txt in leg.get_texts():
        txt.set_color(DIM)
    return _to_png(fig)