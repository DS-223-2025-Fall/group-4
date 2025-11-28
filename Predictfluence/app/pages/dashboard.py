import streamlit as st
from pages.components import kpi_card, placeholder_section
from pages import api
import pandas as pd
import numpy as np

def render(api_url: str):
    st.title("Dashboard")
    st.markdown("Overview • KPIs • Trend charts")

    st.markdown("**Data source:** hooked to backend APIs per docs/app.md.")

    # KPI row
    cols = st.columns(4)

    # Active campaigns
    with cols[0]:
        value = "—"
        if not st.session_state.get('demo_mode'):
            res = api.get('/campaigns', params={'status': 'active'})
            if isinstance(res, dict) and 'items' in res:
                value = str(len(res['items']))
        else:
            value = "12"  # demo fallback
        kpi_card("Active Campaigns", value, "Data: GET /campaigns?status=active")

    # Total influencers
    with cols[1]:
        value = "—"
        if not st.session_state.get('demo_mode'):
            res = api.get('/influencers/count')
            if isinstance(res, dict) and 'count' in res:
                value = str(res['count'])
        else:
            value = "1,452"
        kpi_card("Total Influencers", value, "Data: GET /influencers/count")

    # Avg engagement
    with cols[2]:
        value = "—"
        if not st.session_state.get('demo_mode'):
            res = api.get('/analytics/performance')
            if isinstance(res, dict) and 'avg_engagement_rate' in res:
                value = f"{res['avg_engagement_rate']:.2%}"
        else:
            value = "3.8%"
        kpi_card("Avg Engagement", value, "Field: avg_engagement_rate")

    # Avg cost / influencer
    with cols[3]:
        value = "—"
        if not st.session_state.get('demo_mode'):
            # Aggregate cost KPI not yet available in backend; leave placeholder.
            value = "—"
        else:
            value = "$128"
        kpi_card("Avg Cost / Influencer", value, "Pending backend cost fields")

    st.markdown("### Trends")

    # Engagement over time (line)
    ph1 = placeholder_section("Engagement Over Time", "Fetch from your API: /analytics/engagement?range=30d")
    if st.session_state.get('demo_mode'):
        df = pd.DataFrame({
            'date': pd.date_range(end=pd.Timestamp.today(), periods=30),
            'engagement_rate': (np.sin(np.linspace(0, 3.14, 30)) * 0.5 + 1.5) * 0.02
        }).set_index('date')
        ph1.empty()
        ph1.line_chart(df['engagement_rate'])
    else:
        res = api.get('/analytics/engagement', params={'range': '30d'})
        if res and isinstance(res, dict) and 'series' in res:
            try:
                df = pd.DataFrame(res['series'])
                df = df.set_index(pd.to_datetime(df['date']))
                ph1.empty()
                ph1.line_chart(df['engagement_rate'])
            except Exception:
                ph1.write('Unexpected engagement data format')

    # Top campaigns (bar)
    ph2 = placeholder_section("Top Campaigns", "Fetch from: /analytics/top-campaigns?limit=5")
    if st.session_state.get('demo_mode'):
        df2 = pd.DataFrame({'campaign': ['A','B','C','D','E'], 'engagement': [0.05,0.042,0.038,0.031,0.025]}).set_index('campaign')
        ph2.empty()
        ph2.bar_chart(df2['engagement'])
    else:
        res = api.get('/analytics/top-campaigns', params={'limit': 5})
        if res and isinstance(res, dict) and 'items' in res:
            try:
                df2 = pd.DataFrame(res['items']).set_index('name')
                ph2.empty()
                ph2.bar_chart(df2['metric_value'])
            except Exception:
                ph2.write('Unexpected top-campaigns data format')
