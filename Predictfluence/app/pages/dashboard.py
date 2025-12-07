import streamlit as st
from pages.components import kpi_card, placeholder_section
from pages import api
import pandas as pd
import numpy as np

def render(api_url: str):
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="font-size:32px; font-weight:700; color:#1f2937; margin-bottom:4px;">Dashboard</h1>
        <p style="color:#6b7280; font-size:14px;">Overview • KPIs • Trend charts</p>
    </div>
    """, unsafe_allow_html=True)

    # KPI row
    cols = st.columns(4)

    # Active campaigns
    with cols[0]:
        value = "—"
        if not st.session_state.get('demo_mode'):
            # Try /campaigns/summary first, fallback to /campaigns?status=active
            res = api.get('/campaigns/summary')
            if isinstance(res, dict) and 'active_campaigns' in res:
                value = str(res['active_campaigns'])
            else:
                res = api.get('/campaigns', params={'status': 'active'})
                if isinstance(res, list):
                    value = str(len(res))
        else:
            value = "12"  # demo fallback
        kpi_card("Active Campaigns", value, "Data: GET /campaigns/summary or /campaigns?status=active")

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
            # Try /analytics/performance first, fallback to /campaigns/summary
            res = api.get('/analytics/performance')
            if isinstance(res, dict) and 'avg_cost_per_influencer' in res:
                value = f"${res['avg_cost_per_influencer']:.2f}"
            else:
                res = api.get('/campaigns/summary')
                if isinstance(res, dict) and 'avg_cost_per_influencer' in res:
                    value = f"${res['avg_cost_per_influencer']:.2f}"
        else:
            value = "$128"
        kpi_card("Avg Cost / Influencer", value, "GET /analytics/performance or /campaigns/summary")

    st.markdown("""
    <div style="margin-top:32px; margin-bottom:16px;">
        <h2 style="font-size:24px; font-weight:700; color:#1f2937;">Trends</h2>
    </div>
    """, unsafe_allow_html=True)

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
        if res:
            try:
                df = pd.DataFrame(res)
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
        if res:
            try:
                df2 = pd.DataFrame(res).set_index('campaign')
                ph2.empty()
                ph2.bar_chart(df2['engagement'])
            except Exception:
                ph2.write('Unexpected top-campaigns data format')
