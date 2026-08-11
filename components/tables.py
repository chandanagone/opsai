"""Reusable table rendering helpers."""

import streamlit as st
import pandas as pd


def render_table(df: pd.DataFrame, height: int = 360, empty_message: str = "No records found."):
    if df is None or df.empty:
        st.info(f"ℹ️ {empty_message}")
        return
    st.dataframe(df, use_container_width=True, height=height, hide_index=True)


def paginated_table(df: pd.DataFrame, page_size: int = 10, key: str = "table"):
    if df is None or df.empty:
        st.info("ℹ️ No records found.")
        return
    total_pages = max(1, (len(df) - 1) // page_size + 1)
    page = st.number_input(
        f"Page (1-{total_pages})", min_value=1, max_value=total_pages, value=1, key=f"{key}_page"
    )
    start = (page - 1) * page_size
    st.dataframe(df.iloc[start:start + page_size], use_container_width=True, hide_index=True)
    st.caption(f"Showing {start+1}-{min(start+page_size, len(df))} of {len(df)} records")
