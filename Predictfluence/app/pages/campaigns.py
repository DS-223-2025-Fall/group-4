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
        campaigns = api.get('/campaigns', params={'status':'active'}) or []

    options = ["— none —"] + [f"{c['name']} (id:{c['id']})" for c in campaigns]
    selected_campaign = st.selectbox("Select campaign", options)
    if selected_campaign == "— none —":
        st.info("Select a campaign to view detailed metrics.")
        placeholder_section("Campaign Summary", f"Use GET {api_url}/campaigns/{{id}}/summary to populate.")
    else:
        try:
            cid = int(selected_campaign.split('id:')[-1].strip(')'))
        except Exception:
            cid = None
        placeholder_section("Campaign Summary", f"Use GET {api_url}/campaigns/{cid}/summary to populate.")
        placeholder_section("Influencer Performance", f"Use GET {api_url}/campaigns/{cid}/influencer-performance")
