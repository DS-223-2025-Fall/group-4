# pages/insights.py
import streamlit as st
from pages.components import placeholder_section

def render(api_url: str):
    st.title("Insights & Visualizations")
    st.markdown("Advanced visualizations; hook to analytics endpoints.")

    tab1, tab2 = st.tabs(["Audience Insights", "Creative Insights"])
    with tab1:
        placeholder_section("Audience Demographics", "GET {api_url}/analytics/audience")
    with tab2:
        placeholder_section("Top Creative Types", "GET {api_url}/analytics/creative")
