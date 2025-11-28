import streamlit as st
from pages import api

def render(api_url: str):
    st.title("Welcome — Micro-Influencer Analytics")
    st.markdown("Light mode • rounded UI • demo available")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("Enter your credentials to access the dashboard.")
        username = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            # call centralized auth helper
            res = api.auth_login(username, password)
            if res:
                st.session_state.authenticated = True
                st.success("Login successful.")
                st.experimental_rerun()

    with col2:
        st.markdown("## Preview / Demo")
        if st.button("Preview All Pages (skip login)"):
            st.session_state.demo_mode = True
            st.session_state.authenticated = True
            st.session_state.auth_token = "demo-token"
            st.success("Demo mode enabled. You can browse pages.")
            st.experimental_rerun()

    st.markdown("---")
    st.caption(f"API placeholder: {api_url}")
