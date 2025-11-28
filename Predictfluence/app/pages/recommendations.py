import streamlit as st
from pages.components import placeholder_section
from pages import api

def render(api_url: str):
    st.title("Recommendations")
    st.markdown("AI/algorithmic suggestions — placeholder for future `/recommendations` endpoint.")

    st.subheader("Filters")

    cols = st.columns(4)

    with cols[0]:
        platform = st.selectbox(
            "Platform",
            ["All", "Instagram", "TikTok", "YouTube"]
        )

    with cols[1]:
        audience = st.selectbox(
            "Audience Size",
            ["Any", "1k–10k", "10k–100k", "100k+"]
        )

    with cols[2]:
        content_type = st.selectbox(
            "Content Type",
            [
                "Any",
                "Lifestyle",
                "Beauty",
                "Fashion",
                "Tech",
                "Gaming",
                "Fitness",
                "Travel",
                "Food",
            ]
        )

    with cols[3]:
        run = st.button("Run Recommendations")

    if run:
        payload = {
            'platform': None if platform=='All' else platform,
            'audience_bucket': audience,
            'content_type': None if content_type=='Any' else content_type,
        }
        if st.session_state.get('demo_mode'):
            placeholder_section("Suggested Influencers", f"(demo) top suggestions appear here")
        else:
            res = api.post('/recommendations', payload)
            placeholder_section("Suggested Influencers", f"Results from POST {api_url}/recommendations")
