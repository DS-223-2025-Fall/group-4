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
                    if isinstance(res, dict):
                        df = pd.DataFrame(list(res.items()), columns=[group_by, 'count'])
                        df = df.set_index(group_by)
                        st.bar_chart(df['count'])
                    elif isinstance(res, list):
                        df = pd.DataFrame(res)
                        if group_by in df.columns:
                            df = df.set_index(group_by)
                            st.bar_chart(df['count'] if 'count' in df.columns else df.iloc[:, 0])
                        else:
                            st.dataframe(df)
                    else:
                        st.json(res)
                except Exception:
                    st.error('Unexpected audience data format')
                    st.json(res)
            else:
                st.info(f"Fetch from GET {api_url}/analytics/audience?group_by={group_by}")
    
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
                    if isinstance(res, dict):
                        if 'content_type' in res or 'topic' in res:
                            key = 'content_type' if 'content_type' in res else 'topic'
                            df = pd.DataFrame(list(res[key].items()), columns=[key, 'engagement_rate'])
                            df = df.set_index(key)
                            st.bar_chart(df['engagement_rate'])
                        else:
                            st.json(res)
                    elif isinstance(res, list):
                        df = pd.DataFrame(res)
                        if 'engagement_rate' in df.columns:
                            index_col = 'content_type' if 'content_type' in df.columns else 'topic'
                            if index_col in df.columns:
                                df = df.set_index(index_col)
                                st.bar_chart(df['engagement_rate'])
                            else:
                                st.dataframe(df)
                        else:
                            st.dataframe(df)
                    else:
                        st.json(res)
                except Exception:
                    st.error('Unexpected creative data format')
                    st.json(res)
            else:
                st.info(f"Fetch from GET {api_url}/analytics/creative")
