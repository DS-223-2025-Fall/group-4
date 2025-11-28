import streamlit as st
from pages.components import placeholder_section
from pages import api

def render(api_url: str):
    st.title("Campaigns")
    st.markdown("Campaign performance pages — hook to `/campaigns` APIs.")

    campaigns = None
    if st.session_state.get('demo_mode'):
        campaigns = [{'id': 1, 'name': 'Summer Launch'}, {'id':2,'name':'Holiday Promo'}]
    else:
        res = api.get('/campaigns', params={'status':'active'})
        if isinstance(res, dict) and 'items' in res:
            campaigns = res['items']
        else:
            campaigns = []

    options = ["— none —"] + [f"{c['name']} (id:{c.get('campaign_id', c.get('id'))})" for c in campaigns]
    selected_campaign = st.selectbox("Select campaign", options)
    if selected_campaign == "— none —":
        st.info("Select a campaign to view detailed metrics.")
        placeholder_section("Campaign Summary", f"Use GET {api_url}/campaigns/{{id}}/summary to populate.")
    else:
        try:
            cid = int(selected_campaign.split('id:')[-1].strip(')'))
        except Exception:
            cid = None
        summary_ph = placeholder_section("Campaign Summary", f"GET {api_url}/campaigns/{cid}/summary")
        perf_ph = placeholder_section("Influencer Performance", f"GET {api_url}/campaigns/{cid}/influencer-performance")

        if not st.session_state.get('demo_mode') and cid:
            summary = api.get(f'/campaigns/{cid}/summary')
            if isinstance(summary, dict):
                summary_ph.empty()
                summary_ph.json(summary)

            perf = api.get(f'/campaigns/{cid}/influencer-performance')
            if isinstance(perf, list):
                perf_ph.empty()
                perf_ph.dataframe(perf)
