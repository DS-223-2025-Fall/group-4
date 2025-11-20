import streamlit as st

def render(api_url: str):
    st.title("Welcome — Micro-Influencer Analytics")
    st.markdown("Light mode • rounded UI • demo available")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("Enter your credentials to access the dashboard.")
        username = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            st.session_state.authenticated = True
            st.success("Pretend login success (demo).")
            st.rerun()

    with col2:
        st.markdown("## Preview / Demo")
        if st.button("Preview All Pages (skip login)"):
            st.session_state.demo_mode = True
            st.session_state.authenticated = True
            st.success("Demo mode enabled. You can browse pages.")
            st.rerun()

    st.markdown("---")
    st.caption(f"API placeholder: {api_url}")
