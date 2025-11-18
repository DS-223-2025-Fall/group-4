# pages/dashboard.py
import streamlit as st
from pages.components import kpi_card, placeholder_section

def render(api_url: str):
    st.title("Dashboard")
    st.markdown("Overview • KPIs • Trend charts")
    st.markdown("**How to hook API:** Replace the placeholder code below with requests to your API endpoints, e.g. `GET {api_url}/campaigns/metrics`")

    # KPI row
    cols = st.columns(4)
    with cols[0]:
        kpi_card("Active Campaigns", "—", "Data from /campaigns/active")
    with cols[1]:
        kpi_card("Total Influencers", "—", "Data from /influencers/count")
    with cols[2]:
        kpi_card("Avg Engagement", "—", "Data from /campaigns/engagement")
    with cols[3]:
        kpi_card("Avg Cost / Influencer", "—", "Data from /campaigns/cost")

    st.markdown("### Trends")
    placeholder_section("Engagement Over Time", "Fetch from your API: /analytics/engagement?range=30d")
    placeholder_section("Top Campaigns", "Fetch from: /campaigns/top")
