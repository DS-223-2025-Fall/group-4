import streamlit as st
from pages.components import placeholder_section
from pages import api

def render(api_url: str):
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="font-size:32px; font-weight:700; color:#1f2937; margin-bottom:4px;">Recommendations</h1>
        <p style="color:#6b7280; font-size:14px;">ML-powered influencer recommendations based on engagement predictions.</p>
    </div>
    """, unsafe_allow_html=True)

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
        # Map frontend values to API expected values
        platform_val = None if platform == 'All' else platform
        category_val = None if content_type == 'Any' else content_type
        
        # Map audience size band
        audience_map = {
            '1k–10k': 'micro',
            '10k–100k': 'mid',
            '100k+': 'macro'
        }
        audience_size_band = None
        if audience != 'Any':
            audience_size_band = audience_map.get(audience, None)
        
        payload = {
            'platform': platform_val,
            'category': category_val,
            'audience_size_band': audience_size_band,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        
        if st.session_state.get('demo_mode'):
            demo_results = [
                {'influencer_id': 1, 'influencer_name': 'Alice', 'platform': 'Instagram', 'predicted_engagement': 0.045, 'rationale': 'High engagement in Beauty category'},
                {'influencer_id': 2, 'influencer_name': 'Bob', 'platform': 'TikTok', 'predicted_engagement': 0.038, 'rationale': 'Strong audience match'},
                {'influencer_id': 3, 'influencer_name': 'Cara', 'platform': 'YouTube', 'predicted_engagement': 0.032, 'rationale': 'Good cost-to-engagement ratio'}
            ]
            st.subheader("Suggested Influencers")
            cols = st.columns(min(3, len(demo_results)))
            for col, result in zip(cols, demo_results):
                with col:
                    st.markdown(f"**{result['influencer_name']}**")
                    if result.get('platform'):
                        st.caption(f"Platform: {result['platform']}")
                    st.metric("Predicted Engagement", f"{result['predicted_engagement']:.2%}")
                    st.caption(result['rationale'])
                    if st.button(f"View Details", key=f"demo_{result['influencer_id']}"):
                        st.info(f"Would navigate to influencer {result['influencer_id']} detail page")
        else:
            res = api.post('/recommendations', payload)
            if res and isinstance(res, dict) and 'recommendations' in res:
                recommendations_list = res['recommendations']
                if recommendations_list:
                    st.subheader("Suggested Influencers")
                    cols = st.columns(min(3, len(recommendations_list)))
                    for col, result in zip(cols, recommendations_list):
                        with col:
                            st.markdown(f"**{result.get('influencer_name', 'Unknown')}**")
                            if result.get('platform'):
                                st.caption(f"Platform: {result['platform']}")
                            if 'predicted_engagement' in result:
                                st.metric("Predicted Engagement", f"{result['predicted_engagement']:.2%}")
                            if 'rationale' in result:
                                st.caption(result['rationale'])
                            if 'influencer_id' in result:
                                if st.button(f"View Details", key=f"inf_{result['influencer_id']}"):
                                    st.info(f"Would navigate to influencer {result['influencer_id']} detail page")
                else:
                    st.info("No recommendations found matching your criteria.")
            elif res:
                st.warning(f"Unexpected response format: {res}")
            else:
                st.error(f"Failed to get recommendations from {api_url}/recommendations")
