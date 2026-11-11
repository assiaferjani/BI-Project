"""Graphiques construits à partir des indicateurs déjà calculés."""

import pandas as pd
import plotly.graph_objects as go


def annual_chart(annual: pd.DataFrame) -> go.Figure:
    figure = go.Figure(go.Scatter(
        x=annual["year"].tolist(), y=annual["articles"].tolist(),
        mode="lines+markers", line={"color": "#2563eb", "width": 3},
        name="Articles uniques", hovertemplate="%{x} : %{y:,} articles<extra></extra>",
    ))
    figure.update_layout(xaxis_title="Année du premier dépôt (v1)",
                         yaxis_title="Articles uniques", margin=dict(l=20, r=20, t=20, b=20))
    figure.update_xaxes(dtick=1)
    figure.update_yaxes(rangemode="tozero")
    return figure


def growth_chart(annual: pd.DataFrame) -> go.Figure:
    known = annual.dropna(subset=["change_pct"])
    figure = go.Figure(go.Bar(
        x=known["year"].tolist(), y=known["change_pct"].tolist(),
        marker_color=["#0f766e" if value >= 0 else "#be123c" for value in known["change_pct"]],
        hovertemplate="%{x} : %{y:.2f} %<extra></extra>", name="Variation annuelle",
    ))
    figure.update_layout(xaxis_title="Année", yaxis_title="Variation (%)",
                         margin=dict(l=20, r=20, t=20, b=20))
    figure.update_xaxes(dtick=1)
    return figure


def category_chart(shares: pd.DataFrame) -> go.Figure:
    ordered = shares.sort_values("articles", ascending=True)
    figure = go.Figure(go.Bar(
        x=ordered["articles"].tolist(), y=ordered["category"].tolist(),
        customdata=ordered["share_pct"].tolist(), orientation="h",
        marker_color="#7c3aed", name="Articles par catégorie",
        hovertemplate="%{y} : %{x:,} articles (%{customdata:.2f} %)<extra></extra>",
    ))
    figure.update_layout(xaxis_title="Articles uniques portant la catégorie",
                         yaxis_title="Catégorie", margin=dict(l=20, r=20, t=20, b=20))
    figure.update_xaxes(rangemode="tozero")
    return figure
