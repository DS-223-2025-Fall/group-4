# app.py

import streamlit as st
import os
from importlib import import_module

st.set_page_config(page_title="Micro-Influencer Analytics (UI Preview)",
                   layout="wide", initial_sidebar_state="expanded")

# load API url from env (placeholder for later)
API_URL = os.getenv("API_URL", "http://localhost:8000")
# aesthetic / fonts / colors
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --accent-grad: linear-gradient(90deg,#1fb6ff,#7c4dff);
  }
  body { font-family: "Inter", "Poppins", sans-serif; }
  .sidebar .stButton>button { border-radius: 10px; }
  .kpi-card { border-radius: 12px; padding: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
  .accent { background: var(--accent-grad); -webkit-background-clip: text; color: transparent; }
</style>
""", unsafe_allow_html=True)

# ---------- Navigation config ----------
PAGES = {
    "Login": "pages.login",
    "Dashboard": "pages.dashboard",
    "Influencers": "pages.influencers",
    "Campaigns": "pages.campaigns",
    "Recommendations": "pages.recommendations",
    "Insights": "pages.insights",
    "Settings": "pages.settings",
}

if "page" not in st.session_state:
    st.session_state.page = "Login"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False

# Sidebar (fixed)
with st.sidebar:
    st.markdown("<h2 class='accent'>Micro-Influencer Analytics</h2>", unsafe_allow_html=True)
    st.markdown("Light mode • Teal→Blue accents • Rounded UI")
    # navigation
    page_choice = st.radio("Navigate", list(PAGES.keys()), index=list(PAGES.keys()).index(st.session_state.page))
    st.session_state.page = page_choice

    st.markdown("---")
    if st.session_state.authenticated:
        st.write("Logged in ✓")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.demo_mode = False
            st.session_state.page = "Login"
    else:
        if st.button("Preview All Pages (Demo)"):
            st.session_state.demo_mode = True
            st.session_state.authenticated = True
            st.session_state.page = "Dashboard"
    st.markdown("---")
    st.caption("UI skeleton — API hooks are ready (API_URL env var).")

# Load and run the selected page module
module_path = PAGES.get(st.session_state.page, "pages.login")
try:
    module = import_module(module_path)
    # Each page file must define `render(api_url: str)` function
    module.render(API_URL)
except Exception as e:
    st.error(f"Failed to load page {st.session_state.page}: {e}")
    st.exception(e)
