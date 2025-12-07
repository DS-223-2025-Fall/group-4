import streamlit as st
from pages.components import placeholder_section
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
    mode = st.radio("", ["Table", "Cards"], horizontal=True)

    # Filters
    with st.expander("Filters", expanded=True):
        cols = st.columns([2,2,2,2])
        platform = cols[0].selectbox("Platform", ["All", "Instagram", "TikTok", "YouTube"])
        category = cols[1].selectbox("Category", ["Any","Lifestyle","Beauty","Tech","Gaming","Travel","Food"]) 
        follower_range = cols[2].slider("Followers", 0, 1000000, (1000, 50000), step=1000)
        q = cols[3].text_input("Search (name / handle)")

        if st.button("Apply Filters"):
            st.experimental_rerun()

    influencers_list = []
    if mode == "Table":
        ph = placeholder_section("Influencer Table", "Call GET /influencers with filters and display pandas.DataFrame here.")
        if st.session_state.get('demo_mode'):
            df = pd.DataFrame([{'id':1,'name':'alice','platform':'Instagram','followers':12000,'category':'Beauty'},{'id':2,'name':'bob','platform':'TikTok','followers':54000,'category':'Gaming'}])
            ph.empty()
            influencers_list = df.to_dict('records')
            st.dataframe(df)
        else:
            params = {
                'platform': None if platform=='All' else platform,
                'category': None if category=='Any' else category,
                'min_followers': follower_range[0],
                'max_followers': follower_range[1],
                'q': q or None
            }
            params = {k:v for k,v in params.items() if v is not None}
            res = api.get('/influencers', params=params)
            if res:
                try:
                    df = pd.DataFrame(res)
                    ph.empty()
                    influencers_list = df.to_dict('records')
                    st.dataframe(df)
                except Exception:
                    ph.write('Unexpected influencers data format')
    else:
        ph = placeholder_section("Influencer Cards", "Render influencer cards in a responsive grid. Use columns to layout.")
        if st.session_state.get('demo_mode'):
            cols = st.columns(3)
            demo = [
                {'id': 1, 'name':'Alice', 'handle':'@alice','followers':12000},
                {'id': 2, 'name':'Bob', 'handle':'@bob','followers':54000},
                {'id': 3, 'name':'Cara', 'handle':'@cara','followers':33000},
            ]
            influencers_list = demo
            for col,inf in zip(cols, demo):
                with col:
                    st.markdown(f"**{inf['name']}**")
                    st.write(inf['handle'])
                    st.write(f"{inf['followers']:,} followers")
        else:
            res = api.get('/influencers', params={
                'platform': None if platform=='All' else platform,
                'category': None if category=='Any' else category,
                'min_followers': follower_range[0],
                'max_followers': follower_range[1],
                'q': q or None
            })
            if res:
                try:
                    influencers_list = res if isinstance(res, list) else [res]
                    ph.empty()
                    cols = st.columns(3)
                    for i, inf in enumerate(influencers_list):
                        with cols[i % 3]:
                            st.markdown(f"**{inf.get('name', 'Unknown')}**")
                            st.write(inf.get('handle', ''))
                            st.write(f"{inf.get('followers', 0):,} followers")
                except Exception:
                    ph.write('Unexpected influencers data format')

    # Detail view section
    if influencers_list:
        st.markdown("---")
        st.subheader("Influencer Details")
        inf_options = ["— none —"] + [f"{inf.get('name', 'Unknown')} (id:{inf.get('id', '?')})" for inf in influencers_list]
        selected_inf = st.selectbox("Select influencer to view details", inf_options)
        
        if selected_inf != "— none —":
            try:
                inf_id = int(selected_inf.split('id:')[-1].strip(')'))
            except Exception:
                inf_id = None
            
            if inf_id:
                # Fetch influencer detail with include=performance,audience
                if st.session_state.get('demo_mode'):
                    detail = {
                        'id': inf_id,
                        'name': 'Alice',
                        'handle': '@alice',
                        'platform': 'Instagram',
                        'followers': 12000,
                        'category': 'Beauty',
                        'performance': {'avg_engagement_rate': 0.045, 'total_posts': 120},
                        'audience': {'country': {'US': 0.6, 'GB': 0.2, 'CA': 0.2}}
                    }
                else:
                    detail = api.get(f'/influencers/{inf_id}', params={'include': 'performance,audience'})
                
                if detail:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("### Profile")
                        st.json({k: v for k, v in detail.items() if k not in ['audience', 'content']})
                    
                    # Audience Breakdown
                    with col2:
                        st.markdown("### Audience Breakdown")
                        if 'audience' in detail:
                            audience_data = detail['audience']
                            if isinstance(audience_data, dict):
                                if 'country' in audience_data:
                                    df_aud = pd.DataFrame(list(audience_data['country'].items()), columns=['country', 'percentage'])
                                    df_aud = df_aud.set_index('country')
                                    st.bar_chart(df_aud)
                                elif 'age_group' in audience_data:
                                    df_aud = pd.DataFrame(list(audience_data['age_group'].items()), columns=['age_group', 'percentage'])
                                    df_aud = df_aud.set_index('age_group')
                                    st.bar_chart(df_aud)
                                elif 'gender' in audience_data:
                                    df_aud = pd.DataFrame(list(audience_data['gender'].items()), columns=['gender', 'percentage'])
                                    df_aud = df_aud.set_index('gender')
                                    st.bar_chart(df_aud)
                                else:
                                    st.json(audience_data)
                        else:
                            # Try dedicated audience endpoint
                            if not st.session_state.get('demo_mode'):
                                audience_res = api.get(f'/influencers/{inf_id}/audience')
                                if audience_res:
                                    if isinstance(audience_res, dict):
                                        if 'country' in audience_res:
                                            df_aud = pd.DataFrame(list(audience_res['country'].items()), columns=['country', 'percentage'])
                                            df_aud = df_aud.set_index('country')
                                            st.bar_chart(df_aud)
                                        else:
                                            st.json(audience_res)
                                    else:
                                        st.dataframe(pd.DataFrame(audience_res))
                                else:
                                    st.info(f"Fetch from GET {api_url}/influencers/{inf_id}/audience")
                    
                    # Content List
                    st.markdown("### Content")
                    if st.session_state.get('demo_mode'):
                        demo_content = [
                            {'id': 1, 'type': 'image', 'url': 'https://via.placeholder.com/300', 'engagement': 450},
                            {'id': 2, 'type': 'video', 'url': 'https://via.placeholder.com/300', 'engagement': 680}
                        ]
                        cols = st.columns(2)
                        for col, content in zip(cols, demo_content):
                            with col:
                                st.markdown(f"**{content['type'].title()}**")
                                st.write(f"Engagement: {content['engagement']}")
                    else:
                        content_res = api.get(f'/influencers/{inf_id}/content')
                        if content_res:
                            try:
                                content_list = content_res if isinstance(content_res, list) else [content_res]
                                cols = st.columns(min(3, len(content_list)))
                                for col, content in zip(cols, content_list):
                                    with col:
                                        if 'url' in content and content.get('type') == 'image':
                                            st.image(content['url'], use_container_width=True)
                                        st.markdown(f"**{content.get('type', 'Unknown')}**")
                                        if 'engagement' in content:
                                            st.write(f"Engagement: {content['engagement']}")
                            except Exception:
                                st.json(content_res)
                        else:
                            st.info(f"Fetch from GET {api_url}/influencers/{inf_id}/content")
