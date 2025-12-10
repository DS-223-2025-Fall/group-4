import streamlit as st
from pages import api
import pandas as pd

def render(api_url: str):
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="font-size:32px; font-weight:700; color:#1f2937; margin-bottom:4px;">Influencer Directory</h1>
        <p style="color:#6b7280; font-size:14px;">List and card views for influencers. Hook to `/influencers` endpoints.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("View mode:")
    mode = st.radio("View Mode", ["Table", "Cards"], horizontal=True, label_visibility="visible")

    # Filters
    with st.expander("Filters", expanded=True):
        cols = st.columns([2,2,2,2])
        platform = cols[0].selectbox("Platform", ["All", "Instagram", "TikTok", "YouTube"])
        category = cols[1].selectbox("Category", ["Any", "Fitness", "Athleisure", "Sports", "Wellness", "Lifestyle", "Beauty", "Tech", "Gaming", "Travel", "Food"]) 
        follower_range = cols[2].slider("Followers", 0, 2000000, (0, 2000000), step=1000)
        q = cols[3].text_input("Search (name / handle)")

        if st.button("Apply Filters"):
            st.rerun()

    influencers_list = []
    if mode == "Table":
        # Build base params
        params = {
            'platform': None if platform=='All' else platform,
            'category': None if category=='Any' else category,
            'q': q or None,
            'page_size': 200,  # API max is 200
            'page': 1
        }
        # Only add follower filters if they're not the full range (default is 0-2000000, so no filter)
        if follower_range and (follower_range[0] > 0 or follower_range[1] < 2000000):
            if follower_range[0] > 0:
                params['min_followers'] = follower_range[0]
            if follower_range[1] < 2000000:
                params['max_followers'] = follower_range[1]
        params = {k:v for k,v in params.items() if v is not None}
        res = api.get('/influencers', params=params)
        if res:
            try:
                # API returns {items: [...], total: N}
                if isinstance(res, dict) and 'items' in res:
                    items = res['items']
                    if items and len(items) > 0:
                        df = pd.DataFrame(items)
                        influencers_list = df.to_dict('records')
                        st.dataframe(df, use_container_width=True)
                        st.caption(f"Showing {len(items)} of {res.get('total', len(items))} influencers")
                    else:
                        st.info("No influencers found matching your filters.")
                elif isinstance(res, list):
                    df = pd.DataFrame(res)
                    influencers_list = df.to_dict('records')
                    if not df.empty:
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No influencers found.")
                else:
                    st.warning(f"Unexpected response format: {type(res)}")
                    st.write(res)
            except Exception as e:
                st.error(f'Error displaying influencers: {e}')
                st.write(f"Response type: {type(res)}")
                if isinstance(res, dict):
                    st.dataframe(pd.DataFrame([res]))
                elif isinstance(res, list):
                    st.dataframe(pd.DataFrame(res))
                else:
                    st.write(f"Response: {res}")
        else:
            st.warning("No response from API. Please check if the API service is running.")
    else:
        # Build base params for cards view
        cards_params = {
            'platform': None if platform=='All' else platform,
            'category': None if category=='Any' else category,
            'q': q or None,
            'page_size': 200,  # API max is 200
            'page': 1
        }
        # Only add follower filters if they're not the full range (default is 0-2000000, so no filter)
        if follower_range and (follower_range[0] > 0 or follower_range[1] < 2000000):
            if follower_range[0] > 0:
                cards_params['min_followers'] = follower_range[0]
            if follower_range[1] < 2000000:
                cards_params['max_followers'] = follower_range[1]
        cards_params = {k:v for k,v in cards_params.items() if v is not None}
        res = api.get('/influencers', params=cards_params)
        if res:
            try:
                # API returns {items: [...], total: N}
                if isinstance(res, dict) and 'items' in res:
                    influencers_list = res['items']
                    total = res.get('total', len(influencers_list))
                elif isinstance(res, list):
                    influencers_list = res
                    total = len(influencers_list)
                else:
                    influencers_list = [res] if res else []
                    total = len(influencers_list)
                
                if influencers_list and len(influencers_list) > 0:
                    cols = st.columns(3)
                    for i, inf in enumerate(influencers_list):
                        with cols[i % 3]:
                            st.markdown(f"**{inf.get('name', 'Unknown')}**")
                            st.write(inf.get('username', inf.get('handle', '')))
                            st.write(f"{inf.get('follower_count', inf.get('followers', 0)):,} followers")
                            if inf.get('platform'):
                                st.caption(f"Platform: {inf.get('platform')}")
                            if inf.get('category'):
                                st.caption(f"Category: {inf.get('category')}")
                    st.caption(f"Showing {len(influencers_list)} of {total} influencers")
                else:
                    st.info("No influencers found matching your filters.")
            except Exception as e:
                st.error(f'Unexpected influencers data format: {e}')
                if isinstance(res, dict):
                    if 'items' in res:
                        st.dataframe(pd.DataFrame(res['items']))
                    else:
                        st.dataframe(pd.DataFrame([res]))
                elif isinstance(res, list):
                    st.dataframe(pd.DataFrame(res))
                else:
                    st.write(f"Response: {res}")
        else:
            st.warning("No response from API. Please check if the API service is running.")

    # Detail view section
    if influencers_list:
        st.markdown("---")
        st.subheader("Influencer Details")
        inf_options = ["— none —"]
        for inf in influencers_list:
            if isinstance(inf, dict):
                name = inf.get('name', 'Unknown')
                inf_id = inf.get('influencer_id') or inf.get('id', '?')
                inf_options.append(f"{name} (id:{inf_id})")
            else:
                inf_options.append(f"Influencer {inf}")
        selected_inf = st.selectbox("Select influencer to view details", inf_options)
        
        if selected_inf != "— none —":
            try:
                inf_id = int(selected_inf.split('id:')[-1].strip(')'))
            except (ValueError, AttributeError):
                inf_id = None
            
            if inf_id:
                # Fetch influencer detail with include=performance only
                detail = api.get(f'/influencers/{inf_id}', params={'include': 'performance'})
                
                if detail:
                    # Normalize nested structures (some responses wrap in 'influencer' key)
                    base = detail.get('influencer', detail)
                    perf = detail.get('performance') or base.get('performance')
                    aud = detail.get('audience') or base.get('audience')

                    st.markdown("### Profile")
                    profile_fields = {
                        "Name": base.get('name') or base.get('full_name') or "—",
                        "Handle": base.get('username') or base.get('handle') or "—",
                        "Platform": base.get('platform') or "—",
                        "Followers": f"{base.get('follower_count', base.get('followers', 0)):,}" if base.get('follower_count') or base.get('followers') else "—",
                        "Category": base.get('category') or "—",
                    }
                    for k, v in profile_fields.items():
                        st.write(f"**{k}:** {v}")

                    # Performance metrics
                    if perf and isinstance(perf, dict):
                        st.markdown("#### Performance")
                        colp1, colp2, colp3 = st.columns(3)
                        colp1.metric("Avg Engagement Rate", f"{perf.get('avg_engagement_rate', 0):.2%}" if perf.get('avg_engagement_rate') is not None else "—")
                        colp2.metric("Avg Likes", f"{perf.get('avg_likes', 0):,.0f}" if perf.get('avg_likes') is not None else "—")
                        colp3.metric("Avg Views", f"{perf.get('avg_views', 0):,.0f}" if perf.get('avg_views') is not None else "—")
