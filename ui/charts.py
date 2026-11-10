"""Graphiques construits à partir des indicateurs déjà calculés."""

import pandas as pd
import plotly.graph_objects as go


def style_chart(figure):
    figure.update_layout(
        template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=310, font=dict(family="Arial, sans-serif", size=11, color="#71848c"),
        hoverlabel=dict(bgcolor="#102e39", font_color="#ffffff", bordercolor="#102e39"),
        showlegend=False, bargap=.5,
    )
    figure.update_xaxes(showgrid=False, zeroline=False, tickfont=dict(size=10), title_font=dict(size=10))
    figure.update_yaxes(gridcolor="#edf2f3", zeroline=False, tickfont=dict(size=10), title_font=dict(size=10))
    return figure


def annual_chart(annual: pd.DataFrame) -> go.Figure:
    figure = go.Figure(go.Scatter(
        x=annual["year"].tolist(), y=annual["articles"].tolist(),
        mode="lines+markers", line={"color": "#087f78", "width": 3, "shape": "spline"},
        fill="tozeroy", fillcolor="rgba(8,127,120,.07)",
        marker={"size": 8, "color": "#087f78", "line": {"color": "white", "width": 2}},
        name="Articles uniques", hovertemplate="%{x} : %{y:,} articles<extra></extra>",
    ))
    figure.update_layout(xaxis_title="Année du premier dépôt (v1)",
                         yaxis_title="Articles uniques", margin=dict(l=20, r=20, t=20, b=20))
    figure.update_xaxes(dtick=1)
    figure.update_yaxes(rangemode="tozero")
    return style_chart(figure)


def growth_chart(annual: pd.DataFrame) -> go.Figure:
    known = annual.dropna(subset=["change_pct"])
    figure = go.Figure(go.Bar(
        x=known["year"].tolist(), y=known["change_pct"].tolist(),
        marker_color=["#0f766e" if value >= 0 else "#c36a5c" for value in known["change_pct"]],
        hovertemplate="%{x} : %{y:.2f} %<extra></extra>", name="Variation annuelle",
    ))
    figure.update_layout(xaxis_title="Année", yaxis_title="Variation (%)",
                         margin=dict(l=20, r=20, t=20, b=20))
    figure.update_xaxes(dtick=1)
    return style_chart(figure)


def category_chart(shares: pd.DataFrame) -> go.Figure:
    ordered = shares.sort_values("articles", ascending=True)
    figure = go.Figure(go.Bar(
        x=ordered["articles"].tolist(), y=ordered["category"].tolist(),
        customdata=ordered["share_pct"].tolist(), orientation="h",
        marker_color=[{"cs.AI": "#087f78", "cs.LG": "#285566", "cs.CL": "#90bdb1"}.get(code, "#6c9299") for code in ordered["category"]], name="Articles par catégorie",
        hovertemplate="%{y} : %{x:,} articles (%{customdata:.2f} %)<extra></extra>",
    ))
    figure.update_layout(xaxis_title="Articles uniques portant la catégorie",
                         yaxis_title="Catégorie", margin=dict(l=20, r=20, t=20, b=20))
    figure.update_xaxes(rangemode="tozero")
    return style_chart(figure)
