import streamlit as st
from pages.components import placeholder_section
from pages import api
import pandas as pd

def render(api_url: str):
    st.title("Influencer Directory")
    st.markdown("List and card views for influencers. Hook to `/influencers` endpoints.")

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

    if mode == "Table":
        ph = placeholder_section("Influencer Table", "Call GET /influencers with filters and display pandas.DataFrame here.")
        if st.session_state.get('demo_mode'):
            df = pd.DataFrame([{'id':1,'name':'alice','platform':'Instagram','followers':12000,'category':'Beauty'},{'id':2,'name':'bob','platform':'TikTok','followers':54000,'category':'Gaming'}])
            ph.empty()
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
                    st.dataframe(df)
                except Exception:
                    ph.write('Unexpected influencers data format')
    else:
        ph = placeholder_section("Influencer Cards", "Render influencer cards in a responsive grid. Use columns to layout.")
        if st.session_state.get('demo_mode'):
            cols = st.columns(3)
            demo = [
                {'name':'Alice', 'handle':'@alice','followers':12000},
                {'name':'Bob', 'handle':'@bob','followers':54000},
                {'name':'Cara', 'handle':'@cara','followers':33000},
            ]
            for col,inf in zip(cols, demo):
                with col:
                    st.markdown(f"**{inf['name']}**")
                    st.write(inf['handle'])
                    st.write(f"{inf['followers']:,} followers")
        else:
            res = api.get('/influencers')
            ph.write('Cards view requires frontend rendering of returned list')
