# pages/campaigns.py
import streamlit as st
from pages.components import placeholder_section

def render(api_url: str):
    st.title("Campaigns")
    st.markdown("Campaign performance pages — hook to `/campaigns` APIs.")

    selected_campaign = st.selectbox("Select campaign (placeholder)", ["— none —"])
    if selected_campaign == "— none —":
        st.info("Select a campaign to view detailed metrics (placeholder).")
    placeholder_section("Campaign Summary", "Use GET {api_url}/campaigns/{id}/summary to populate.")
    placeholder_section("Influencer Performance", "Use GET {api_url}/campaigns/{id}/influencer-performance")
