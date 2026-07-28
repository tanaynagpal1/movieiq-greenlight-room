"""Plotly chart factory for MovieIQ. One function per figure, all sharing
one visual template so every chart in the app looks like it belongs together."""
import plotly.graph_objects as go

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