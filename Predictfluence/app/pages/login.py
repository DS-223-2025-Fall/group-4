import streamlit as st
from pages import api

def render(api_url: str):
    st.markdown("""
    <div class="login-wrap">
        <div class="login-card">
            <h1 style="font-size:28px; font-weight:700; margin-bottom:8px; color:#1f2937;">Welcome to InfluenceIQ</h1>
            <p style="color:#6b7280; font-size:14px; margin-bottom:24px;">Micro-Influencer Analytics Platform</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### Sign In")
        st.markdown("Enter your credentials to access the dashboard.")
        email = st.text_input("Email", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        if st.button("Login", use_container_width=True):
            # Input validation
            if not email or len(email.strip()) == 0:
                st.error("Email is required")
            elif '@' not in email or '.' not in email.split('@')[1]:
                st.error("Please enter a valid email address")
            elif not password or len(password.strip()) == 0:
                st.error("Password is required")
            else:
                # call centralized auth helper
                res = api.auth_login(email.strip(), password)
                if res:
                    st.session_state.authenticated = True
                    st.success("Login successful.")
                    st.rerun()
                else:
                    st.error("Login failed. Please check your credentials.")

    with col2:
        st.markdown("### Preview / Demo")
        st.markdown("Try the platform without credentials")
        if st.button("Preview All Pages (skip login)", use_container_width=True):
            st.session_state.demo_mode = True
            st.session_state.authenticated = True
            st.session_state.auth_token = "demo-token"
            st.success("Demo mode enabled. You can browse pages.")
            st.rerun()

    st.markdown("---")
    st.caption(f"API endpoint: {api_url}")
