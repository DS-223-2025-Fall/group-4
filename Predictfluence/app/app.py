import streamlit as st
import os
from importlib import import_module
from pages.components import inject_styles

st.set_page_config(page_title="Micro-Influencer Analytics (UI Preview)",
                   layout="wide", initial_sidebar_state="expanded")

# load API url from env (placeholder for later)
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Inject global theme styles (applies to all pages)
inject_styles()

# ---------- Navigation config ----------
PAGES = {
    "Demo Intro": "pages.demo",
    "Dashboard": "pages.dashboard",
    "Influencers": "pages.influencers",
    "Campaigns": "pages.campaigns",
    "Recommendations": "pages.recommendations",
    "Insights": "pages.insights",
}

# default session state (always use real API)
if "page" not in st.session_state:
    st.session_state.page = "Demo Intro"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = True
# Always use real API - no demo mode
st.session_state.demo_mode = False
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "prefill_influencer_id" not in st.session_state:
    st.session_state.prefill_influencer_id = None

# Sidebar (fixed)
with st.sidebar:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; margin-top:6px; margin-bottom:12px;">
          <div style="width:38px; height:38px; border-radius:12px; background:linear-gradient(135deg,#12c2e9,#2f80ed); display:flex; align-items:center; justify-content:center; color:#fff; font-weight:800;">
            IQ
          </div>
          <div>
            <div style="font-weight:800; font-size:16px;">InfluenceIQ</div>
            <div style="font-size:12px; color:#6b7280;">Analytics Platform</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    nav_items = list(PAGES.keys())
    page_choice = st.radio(
        "Navigate",
        nav_items,
        index=nav_items.index(st.session_state.page),
        label_visibility="collapsed",
    )
    st.session_state.page = page_choice

    st.markdown("---")
    st.write("Using Live API")
    st.markdown("---")
    st.markdown(
        """
        <div class="iq-card" style="padding:12px;">
          <div style="font-weight:700; font-size:13px; margin-bottom:4px;">Need help?</div>
          <div style="font-size:12px; color:#6b7280;">Check docs or use demo mode.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )




# Initialize API helper (safe to import even if pages not yet loaded)
try:
    from pages import api as api_client
    api_client.init(API_URL)
except Exception:
    # if pages/api.py isn't present yet, we'll still continue — modules will import it when needed
    pass

# Load and run the selected page module
module_path = PAGES.get(st.session_state.page, "pages.login")
try:
    module = import_module(module_path)
    # Each page file must define `render(api_url: str)` function
    module.render(API_URL)
except Exception as e:
    st.error(f"Failed to load page {st.session_state.page}: {e}")
    st.exception(e)
