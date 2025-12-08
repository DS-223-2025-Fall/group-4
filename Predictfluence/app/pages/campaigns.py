import streamlit as st
from pages.components import placeholder_section
from pages import api
import pandas as pd

def render(api_url: str):
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="font-size:32px; font-weight:700; color:#1f2937; margin-bottom:4px;">Campaigns</h1>
        <p style="color:#6b7280; font-size:14px;">Campaign performance pages — hook to `/campaigns` APIs.</p>
    </div>
    """, unsafe_allow_html=True)

    campaigns = []
    if st.session_state.get('demo_mode'):
        campaigns = [{'id': 1, 'name': 'Summer Launch'}, {'id':2,'name':'Holiday Promo'}]
    else:
        # Support both active and all campaigns
        res = api.get('/campaigns', params={'status':'active'})
        if isinstance(res, dict) and 'items' in res:
            campaigns = res['items']
        elif isinstance(res, list):
            campaigns = res
        if not campaigns:
            res = api.get('/campaigns')
            if isinstance(res, dict) and 'items' in res:
                campaigns = res['items']
            elif isinstance(res, list):
                campaigns = res

    # Safely build options list
    options = ["— none —"]
    for c in campaigns:
        if isinstance(c, dict):
            name = c.get('name', 'Unknown')
            cid = c.get('campaign_id') or c.get('id', '?')
            options.append(f"{name} (id:{cid})")
        else:
            options.append(f"Campaign {c}")
    selected_campaign = st.selectbox("Select campaign", options)
    if selected_campaign == "— none —":
        st.info("Select a campaign to view detailed metrics.")
    else:
        try:
            cid = int(selected_campaign.split('id:')[-1].strip(')'))
        except Exception:
            cid = None
        
        if cid:
            # Campaign Summary
            st.subheader("Campaign Summary")
            if st.session_state.get('demo_mode'):
                st.json({
                    'name': 'Summer Launch',
                    'status': 'active',
                    'total_influencers': 15,
                    'total_engagement': 125000,
                    'total_cost': 5000
                })
            else:
                summary = api.get(f'/campaigns/{cid}/summary')
                if summary:
                    st.json(summary)
            
            # Influencer Performance Table
            st.subheader("Influencer Performance")
            if st.session_state.get('demo_mode'):
                demo_df = pd.DataFrame([
                    {'name': 'Alice', 'role': 'Primary', 'paid': True, 'engagement_rate': 0.045, 'reach': 12000},
                    {'name': 'Bob', 'role': 'Secondary', 'paid': False, 'engagement_rate': 0.032, 'reach': 8500}
                ])
                st.dataframe(demo_df)
            else:
                perf = api.get(f'/campaigns/{cid}/influencer-performance')
                if perf:
                    try:
                        df = pd.DataFrame(perf)
                        st.dataframe(df)
                    except Exception:
                        st.error('Unexpected influencer performance data format')
