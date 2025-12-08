import streamlit as st
from pages.components import placeholder_section
from pages import api
import pandas as pd

def render(api_url: str):
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="font-size:32px; font-weight:700; color:#1f2937; margin-bottom:4px;">Insights & Visualizations</h1>
        <p style="color:#6b7280; font-size:14px;">Advanced visualizations; hook to analytics endpoints.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Audience Insights", "Creative Insights"])
    with tab1:
        st.subheader("Audience Demographics")
        group_by = st.selectbox("Group by", ["country", "age_group", "gender"], key="audience_group")
        
        if st.session_state.get('demo_mode'):
            if group_by == 'country':
                df = pd.DataFrame({'country':['US','GB','IN','CA'],'count':[1200,340,890,210]}).set_index('country')
                st.bar_chart(df['count'])
            elif group_by == 'age_group':
                df = pd.DataFrame({'age_group':['18-24','25-34','35-44','45+'],'count':[800,600,400,200]}).set_index('age_group')
                st.bar_chart(df['count'])
            else:
                df = pd.DataFrame({'gender':['Female','Male','Other'],'count':[1200,800,100]}).set_index('gender')
                st.bar_chart(df['count'])
        else:
            res = api.get('/analytics/audience', params={'group_by': group_by})
            if res:
                try:
                    if isinstance(res, dict) and 'items' in res:
                        # API returns {group_by: "country", items: [{group: "USA", percentage: 25.5}]}
                        items = res['items']
                        if items:
                            df = pd.DataFrame(items)
                            if 'group' in df.columns and 'percentage' in df.columns:
                                df = df.set_index('group')
                                st.bar_chart(df['percentage'])
                            else:
                                st.dataframe(df)
                        else:
                            st.info("No audience data available")
                    elif isinstance(res, list):
                        df = pd.DataFrame(res)
                        if group_by in df.columns:
                            df = df.set_index(group_by)
                            st.bar_chart(df['percentage'] if 'percentage' in df.columns else df.iloc[:, 0])
                        else:
                            st.dataframe(df)
                    else:
                        st.json(res)
                except Exception as e:
                    st.error(f'Unexpected audience data format: {e}')
                    st.json(res)
    
    with tab2:
        st.subheader("Creative Performance")
        if st.session_state.get('demo_mode'):
            df_creative = pd.DataFrame({
                'content_type': ['Image', 'Video', 'Reel', 'Story'],
                'engagement_rate': [0.035, 0.042, 0.048, 0.028]
            }).set_index('content_type')
            st.bar_chart(df_creative['engagement_rate'])
        else:
            res = api.get('/analytics/creative')
            if res:
                try:
                    if isinstance(res, dict) and 'items' in res:
                        # API returns {items: [{content_type: "Image", avg_engagement_rate: 0.035}]}
                        items = res['items']
                        if items:
                            df = pd.DataFrame(items)
                            # Check for avg_engagement_rate (API field) or engagement_rate (fallback)
                            engagement_col = 'avg_engagement_rate' if 'avg_engagement_rate' in df.columns else 'engagement_rate'
                            if 'content_type' in df.columns and engagement_col in df.columns:
                                df = df.set_index('content_type')
                                st.bar_chart(df[engagement_col])
                            elif 'topic' in df.columns and engagement_col in df.columns:
                                df = df.set_index('topic')
                                st.bar_chart(df[engagement_col])
                            else:
                                st.dataframe(df)
                        else:
                            st.info("No creative data available")
                    elif isinstance(res, list):
                        df = pd.DataFrame(res)
                        engagement_col = 'avg_engagement_rate' if 'avg_engagement_rate' in df.columns else 'engagement_rate'
                        if engagement_col in df.columns:
                            index_col = 'content_type' if 'content_type' in df.columns else 'topic'
                            if index_col in df.columns:
                                df = df.set_index(index_col)
                                st.bar_chart(df[engagement_col])
                            else:
                                st.dataframe(df)
                        else:
                            st.dataframe(df)
                    else:
                        st.json(res)
                except Exception as e:
                    st.error(f'Unexpected creative data format: {e}')
                    st.json(res)
