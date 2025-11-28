import streamlit as st
from pages.components import placeholder_section
from pages import api

def render(api_url: str):
    st.title("Insights & Visualizations")
    st.markdown("Advanced visualizations; hook to analytics endpoints.")

    tab1, tab2 = st.tabs(["Audience Insights", "Creative Insights"])
    with tab1:
        ph = placeholder_section("Audience Demographics", "GET {api_url}/analytics/audience?group_by=country|age_group|gender")
        if st.session_state.get('demo_mode'):
            import pandas as pd
            df = pd.DataFrame({'country':['US','GB','IN','CA'],'count':[1200,340,890,210]}).set_index('country')
            ph.empty(); ph.bar_chart(df['count'])
    with tab2:
        placeholder_section("Top Creative Types", "GET {api_url}/analytics/creative — show engagement by content type/topic")
