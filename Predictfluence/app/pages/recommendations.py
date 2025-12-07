import streamlit as st
from pages.components import placeholder_section
from pages import api

def render(api_url: str):
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="font-size:32px; font-weight:700; color:#1f2937; margin-bottom:4px;">Recommendations</h1>
        <p style="color:#6b7280; font-size:14px;">AI/algorithmic suggestions — placeholder for future `/recommendations` endpoint.</p>
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
        payload = {
            'platform': None if platform=='All' else platform,
            'audience_bucket': audience if audience != 'Any' else None,
            'content_type': None if content_type=='Any' else content_type,
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        
        if st.session_state.get('demo_mode'):
            demo_results = [
                {'id': 1, 'name': 'Alice', 'handle': '@alice', 'predicted_engagement': 0.045, 'rationale': 'High engagement in Beauty category'},
                {'id': 2, 'name': 'Bob', 'handle': '@bob', 'predicted_engagement': 0.038, 'rationale': 'Strong audience match'},
                {'id': 3, 'name': 'Cara', 'handle': '@cara', 'predicted_engagement': 0.032, 'rationale': 'Good cost-to-engagement ratio'}
            ]
            st.subheader("Suggested Influencers")
            cols = st.columns(3)
            for col, result in zip(cols, demo_results):
                with col:
                    st.markdown(f"**{result['name']}** {result['handle']}")
                    st.metric("Predicted Engagement", f"{result['predicted_engagement']:.2%}")
                    st.caption(result['rationale'])
                    if st.button(f"View Details", key=f"demo_{result['id']}"):
                        st.info(f"Would navigate to influencer {result['id']} detail page")
        else:
            res = api.post('/recommendations', payload)
            if res:
                st.subheader("Suggested Influencers")
                results_list = res if isinstance(res, list) else [res]
                cols = st.columns(min(3, len(results_list)))
                for col, result in zip(cols, results_list):
                    with col:
                        st.markdown(f"**{result.get('name', 'Unknown')}** {result.get('handle', '')}")
                        if 'predicted_engagement' in result:
                            st.metric("Predicted Engagement", f"{result['predicted_engagement']:.2%}")
                        if 'rationale' in result:
                            st.caption(result['rationale'])
                        if 'id' in result:
                            if st.button(f"View Details", key=f"inf_{result['id']}"):
                                st.info(f"Would navigate to influencer {result['id']} detail page")
            else:
                st.info(f"Results from POST {api_url}/recommendations")
