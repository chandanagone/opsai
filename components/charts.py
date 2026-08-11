"""Reusable Plotly chart builder functions with a consistent theme."""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

THEME_COLORS = ["#2563eb", "#16a34a", "#d97706", "#dc2626", "#0284c7", "#7c3aed"]


def _apply_layout(fig, title=None, height=320):
    fig.update_layout(
        title=title,
        height=height,
        margin=dict(l=10, r=10, t=40 if title else 10, b=10),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        font=dict(color="#334155", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
    return fig


def line_chart(df, x, y, title=None, color=None, height=320):
    if df is None or df.empty:
        return empty_chart(title)
    fig = px.line(df, x=x, y=y, color=color, markers=True, color_discrete_sequence=THEME_COLORS)
    return _apply_layout(fig, title, height)


def bar_chart(df, x, y, title=None, color=None, height=320, orientation="v"):
    if df is None or df.empty:
        return empty_chart(title)
    fig = px.bar(df, x=x, y=y, color=color, orientation=orientation, color_discrete_sequence=THEME_COLORS)
    return _apply_layout(fig, title, height)


def area_chart(df, x, y, title=None, height=320):
    if df is None or df.empty:
        return empty_chart(title)
    fig = px.area(df, x=x, y=y, color_discrete_sequence=THEME_COLORS)
    return _apply_layout(fig, title, height)


def pie_chart(df, names, values, title=None, height=320):
    if df is None or df.empty:
        return empty_chart(title)
    fig = px.pie(df, names=names, values=values, hole=0.45, color_discrete_sequence=THEME_COLORS)
    return _apply_layout(fig, title, height)


def empty_chart(title=None, message="No data available for the selected filters"):
    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(size=13, color="#94a3b8"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _apply_layout(fig, title, height=280)
