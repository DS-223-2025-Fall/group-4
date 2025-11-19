# pages/influencers.py
import streamlit as st
from pages.components import placeholder_section

def render(api_url: str):
    st.title("Influencer Directory")
    st.markdown("List and card views for influencers. Hook to `/influencers` endpoints.")

    st.write("View mode:")
    mode = st.radio("", ["Table", "Cards"], horizontal=True)

    if mode == "Table":
        placeholder_section("Influencer Table", "Call GET {api_url}/influencers and display pandas.DataFrame here.")
    else:
        placeholder_section("Influencer Cards", "Render influencer cards in a responsive grid. Use columns to layout.")
