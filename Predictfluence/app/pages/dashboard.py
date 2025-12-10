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

    # Export buttons
    col1, col2, col3 = st.columns([1, 1, 6])
    with col1:
        if st.button("Export Influencers"):
            import requests
            try:
                response = requests.get(f"{api_url}/export/influencers", timeout=10)
                if response.status_code == 200:
                    st.download_button(
                        label="Download CSV",
                        data=response.content,
                        file_name="influencers.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Failed to export: {str(e)}")
    with col2:
        if st.button("Export Campaigns"):
            import requests
            try:
                response = requests.get(f"{api_url}/export/campaigns", timeout=10)
                if response.status_code == 200:
                    st.download_button(
                        label="Download CSV",
                        data=response.content,
                        file_name="campaigns.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.error(f"Failed to export: {str(e)}")

    # KPI row with clarity on definitions
    cols = st.columns(4)

    # Total campaigns (all statuses)
    with cols[0]:
        value = "—"
        res = api.get('/campaigns')  # Get all campaigns, not just active
        if res:
            if isinstance(res, dict) and 'items' in res:
                value = str(len(res['items']))
            elif isinstance(res, list):
                value = str(len(res))
        kpi_card("Total Campaigns", value)

    # Total influencers
    with cols[1]:
        value = "—"
        try:
            res = api.get('/influencers/count')
            if res:
                if isinstance(res, dict) and 'count' in res:
                    value = str(res['count'])
                elif isinstance(res, int):
                    value = str(res)
        except Exception:
            value = "—"
        kpi_card("Total Influencers", value)

    # Avg engagement
    with cols[2]:
        value = "—"
        res = api.get('/analytics/performance')
        if res and isinstance(res, dict) and 'avg_engagement_rate' in res:
            value = f"{res['avg_engagement_rate']:.2%}"
        kpi_card("Avg Engagement (rate)", value)
        st.caption("Avg engagement rate across recent influencer content.")

    # Avg cost / influencer
    with cols[3]:
        value = "—"
        try:
            res = api.get('/analytics/performance')
            if res and isinstance(res, dict) and 'avg_cost_per_influencer' in res:
                cost = res['avg_cost_per_influencer']
                if cost and cost > 0:
                    value = f"${cost:,.2f}"
        except Exception:
            value = "—"
        kpi_card("Avg Cost / Influencer", value)
        st.caption("Avg campaign spend divided by unique influencers engaged.")

    st.markdown("""
    <div style="margin-top:32px; margin-bottom:16px;">
        <h2 style="font-size:24px; font-weight:700; color:#1f2937;">Trends</h2>
    </div>
    """, unsafe_allow_html=True)

    # Engagement over time (line)
    ph1 = placeholder_section("Engagement Over Time (last 30 days)")
    res = api.get('/analytics/engagement', params={'range': '30d'})
    if res:
        try:
            if isinstance(res, dict) and 'series' in res:
                df = pd.DataFrame(res['series'])
            elif isinstance(res, list):
                df = pd.DataFrame(res)
            else:
                df = pd.DataFrame(res)
            if not df.empty and 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df = df.set_index('date')
                if 'engagement_rate' in df.columns:
                    ph1.empty()
                    ph1.line_chart(df['engagement_rate'])
                else:
                    ph1.write('Missing engagement_rate column')
            else:
                ph1.write('No engagement data available')
        except Exception as e:
            ph1.write(f'Unexpected engagement data format: {e}')
            if res:
                if isinstance(res, dict):
                    ph1.dataframe(pd.DataFrame([res]))
                elif isinstance(res, list):
                    ph1.dataframe(pd.DataFrame(res))
                else:
                    ph1.write(f"Data: {res}")
    else:
        ph1.write('No engagement data available')

    # Top campaigns (bar)
    ph2 = placeholder_section("Top Campaigns by engagement rate")
    res = api.get('/analytics/top-campaigns', params={'limit': 5})
    if res:
        try:
            if isinstance(res, dict) and 'items' in res:
                items = res['items']
                df2 = pd.DataFrame(items)
            elif isinstance(res, list):
                df2 = pd.DataFrame(res)
            else:
                df2 = pd.DataFrame(res)
            if not df2.empty:
                # Find campaign name column
                campaign_col = None
                for col in ['campaign', 'name', 'campaign_name']:
                    if col in df2.columns:
                        campaign_col = col
                        break
                if campaign_col:
                    df2 = df2.set_index(campaign_col)
                # Find engagement metric column
                engagement_col = None
                for col in ['engagement', 'engagement_rate', 'metric_value', 'value']:
                    if col in df2.columns:
                        engagement_col = col
                        break
                if engagement_col:
                    ph2.empty()
                    ph2.bar_chart(df2[engagement_col])
                else:
                    ph2.dataframe(df2)
            else:
                ph2.write('No campaign data available')
        except Exception as e:
            ph2.write(f'Unexpected top-campaigns data format: {e}')
            if res:
                if isinstance(res, dict):
                    ph2.dataframe(pd.DataFrame([res]))
                elif isinstance(res, list):
                    ph2.dataframe(pd.DataFrame(res))
                else:
                    ph2.write(f"Data: {res}")
    else:
        ph2.write('No campaign data available')
