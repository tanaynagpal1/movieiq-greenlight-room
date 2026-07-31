"""Plotly chart factory for MovieIQ. One function per figure, all sharing
one visual template so every chart in the app looks like it belongs together."""
import plotly.graph_objects as go
import numpy as np
from src.loader import BUDGET_BANDS

TEAL = "#2BD9C4"
GOLD = "#C9A227"
PURPLE = "#9D5CFF"
RED = "#E0526B"
GRID = "#1E1830"
TEXT = "#9089AB"


def _style(fig, height=360):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT, size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        hoverlabel=dict(bgcolor="#171123", bordercolor="#2A2038"),
        legend=dict(orientation="h", y=1.08, x=0, font=dict(color=TEXT)),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    return fig


def breakeven_scatter(df):
    """Budget vs Revenue, gold break-even line at revenue = budget."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.loc[df.success == 1, "budget"] / 1e6,
        y=df.loc[df.success == 1, "revenue"] / 1e6,
        mode="markers", name="Profitable",
        marker=dict(color=TEAL, size=6, opacity=0.55, line=dict(width=0)),
    ))
    fig.add_trace(go.Scatter(
        x=df.loc[df.success == 0, "budget"] / 1e6,
        y=df.loc[df.success == 0, "revenue"] / 1e6,
        mode="markers", name="Loss",
        marker=dict(color=RED, size=6, opacity=0.6, line=dict(width=0)),
    ))
    top = max(df.budget.max(), df.revenue.max()) / 1e6
    fig.add_trace(go.Scatter(
        x=[0, top], y=[0, top], mode="lines", name="Break-even",
        line=dict(color=GOLD, width=2, dash="dash"),
    ))
    fig.update_xaxes(title="Budget ($M)")
    fig.update_yaxes(title="Revenue ($M)")
    return _style(fig)


def genre_success_bar(df):
    """Success rate by genre — shows every genre clusters near the same rate."""
    agg = df.groupby("genre")["success"].agg(["mean", "count"]).reset_index()
    agg = agg.sort_values("mean", ascending=True)
    fig = go.Figure(go.Bar(
        x=agg["mean"] * 100, y=agg["genre"], orientation="h",
        marker=dict(color=GOLD),
        text=[f"{v:.1f}%" for v in agg["mean"] * 100],
        textposition="outside", textfont=dict(color=TEXT),
    ))
    fig.add_vline(x=df.success.mean() * 100, line_dash="dot",
               line_color=PURPLE, annotation_text="overall avg",
               annotation_font_color=PURPLE,
               annotation_position="top left")
    fig.update_xaxes(title="Success rate (%)")
    fig.update_yaxes(title="")
    return _style(fig, height=420)


def correlation_heatmap(df):
    """Correlation matrix of the four usable numeric features plus success."""
    cols = ["budget", "popularity", "runtime", "vote_average", "success"]
    corr = df[cols].corr().round(2)
    fig = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.columns,
        colorscale=[[0, RED], [0.5, "#171123"], [1, TEAL]],
        zmid=0, zmin=-1, zmax=1,
        text=corr.values, texttemplate="%{text}",
        textfont=dict(color="#EDE9F5", size=11),
        colorbar=dict(tickfont=dict(color=TEXT)),
    ))
    return _style(fig, height=380)


def profit_distribution_chart(profits):
    """Simulated profit distribution: loss outcomes shaded red,
    profit outcomes violet, with a gold needle at break-even (profit = 0)."""
    bins = np.linspace(profits.min(), profits.max(), 60)
    centers = (bins[:-1] + bins[1:]) / 2
    counts_loss, _ = np.histogram(profits[profits <= 0], bins=bins)
    counts_profit, _ = np.histogram(profits[profits > 0], bins=bins)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=centers, y=counts_loss, name="Loss",
                          marker=dict(color=RED)))
    fig.add_trace(go.Bar(x=centers, y=counts_profit, name="Profit",
                          marker=dict(color=PURPLE)))
    fig.add_vline(x=0, line_dash="dash", line_color=GOLD,
                  annotation_text="break-even", annotation_font_color=GOLD)
    fig.update_layout(barmode="overlay", bargap=0)
    fig.update_xaxes(title="Simulated profit ($)")
    fig.update_yaxes(title="Count")
    return _style(fig, height=340)


def slate_roi_chart(roi_dict):
    """Overlaid density of portfolio ROI at different slate sizes.
    roi_dict: {slate_size (int): np.ndarray of portfolio ROI outcomes}."""
    colors = {1: RED, 5: GOLD, 20: TEAL}
    fig = go.Figure()
    for size, roi in sorted(roi_dict.items()):
        fig.add_trace(go.Histogram(
            x=roi, histnorm="probability density",
            name=f"{size}-film slate",
            marker=dict(color=colors.get(size, PURPLE)),
            opacity=0.55,
        ))
    fig.add_vline(x=0, line_dash="dash", line_color="#EDE9F5",
                  annotation_text="break-even")
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(title="Portfolio ROI")
    fig.update_yaxes(title="Density")
    return _style(fig, height=380)


GENRE_PALETTE = [
    TEAL, GOLD, PURPLE, RED, "#5EC8D8", "#E8C468",
    "#B98CFF", "#F08497", "#4FA88F", "#9089AB",
]


def _genre_colors(genres):
    return {g: GENRE_PALETTE[i % len(GENRE_PALETTE)] for i, g in enumerate(sorted(genres))}


def genre_share_donut(df):
    """Composition of the catalogue by genre — how many films of each type."""
    counts = df["genre"].value_counts()
    colors = _genre_colors(counts.index)
    fig = go.Figure(go.Pie(
        labels=counts.index, values=counts.values, hole=0.55,
        marker=dict(colors=[colors[g] for g in counts.index],
                    line=dict(color="#07060B", width=2)),
        textfont=dict(color="#EDE9F5", size=11),
        textinfo="label+percent",
    ))
    fig.update_layout(showlegend=False)
    return _style(fig, height=380)


def outcome_donut(df):
    """Share of films that were profitable vs a loss."""
    counts = df["success"].value_counts().reindex([1, 0]).fillna(0)
    fig = go.Figure(go.Pie(
        labels=["Profitable", "Loss"], values=counts.values, hole=0.55,
        marker=dict(colors=[TEAL, RED], line=dict(color="#07060B", width=2)),
        textfont=dict(color="#EDE9F5", size=12),
        textinfo="label+percent",
    ))
    fig.update_layout(showlegend=False)
    return _style(fig, height=320)


def budget_band_performance(df):
    """Success rate by budget category, in defined dollar order (not
    alphabetical) — 'Blockbuster' should not sort above 'Micro/Indie'."""
    order = [b for b in BUDGET_BANDS if b in set(df["budget_band"])]
    agg = df.groupby("budget_band")["success"].mean().reindex(order)
    fig = go.Figure(go.Bar(
        x=agg.index, y=agg.values * 100,
        marker=dict(color=[TEAL, GOLD, PURPLE, RED][:len(agg)]),
        text=[f"{v:.1f}%" for v in agg.values * 100],
        textposition="outside", textfont=dict(color=TEXT),
    ))
    fig.add_hline(y=df["success"].mean() * 100, line_dash="dot",
                   line_color="#9089AB")
    fig.update_yaxes(title="Success rate (%)")
    fig.update_xaxes(title="")
    return _style(fig, height=340)


def distribution_histogram(df, column, title, color=TEAL, prefix="", suffix=""):
    """Reusable histogram for any numeric column — budget, ROI, runtime, rating."""
    vals = df[column]
    fig = go.Figure(go.Histogram(
        x=vals, marker=dict(color=color, line=dict(color="#07060B", width=0.5)),
        nbinsx=40,
    ))
    fig.add_vline(x=vals.median(), line_dash="dash", line_color=GOLD,
                   annotation_text=f"median {prefix}{vals.median():,.1f}{suffix}",
                   annotation_font_color=GOLD, annotation_position="top right")
    fig.update_xaxes(title=title)
    fig.update_yaxes(title="Count")
    return _style(fig, height=320)


def genre_box(df, column, title):
    """Box plot of a numeric column split by genre — median, spread, outliers."""
    order = df.groupby("genre")[column].median().sort_values().index
    colors = _genre_colors(order)
    fig = go.Figure()
    for g in order:
        fig.add_trace(go.Box(
            y=df.loc[df.genre == g, column], name=g,
            marker=dict(color=colors[g]), line=dict(color=colors[g]),
            boxpoints=False,
        ))
    fig.update_layout(showlegend=False)
    fig.update_yaxes(title=title)
    return _style(fig, height=380)


def runtime_vs_rating_bubble(df):
    """Runtime vs rating, colored by genre, bubble size by budget — the
    combined-signal EDA view: does anything visually cluster by genre?"""
    colors = _genre_colors(df["genre"].unique())
    fig = go.Figure()
    for g in sorted(df["genre"].unique()):
        sub = df[df.genre == g]
        fig.add_trace(go.Scatter(
            x=sub["runtime"], y=sub["vote_average"], mode="markers", name=g,
            marker=dict(
                color=colors[g], size=(sub["budget"] / df["budget"].max() * 22 + 4),
                opacity=0.55, line=dict(width=0),
            ),
            hovertext=sub["title"], hoverinfo="text",
        ))
    fig.update_xaxes(title="Runtime (min)")
    fig.update_yaxes(title="Vote average")
    return _style(fig, height=420)