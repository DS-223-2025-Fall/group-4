# pages/components.py
import streamlit as st

def kpi_card(title: str, value: str, subtitle: str = ""):
    """Small KPI-styled card used on dashboard."""
    card = st.container()
    with card:
        st.markdown(f"""
        <div class="kpi-card">
          <div style="display:flex; justify-content:space-between;">
            <div>
              <div style="font-size:14px; color:#6b7280;">{title}</div>
              <div style="font-size:22px; font-weight:700;">{value}</div>
              <div style="font-size:12px; color:#9ca3af;">{subtitle}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

def placeholder_section(title: str, description: str = None):
    st.subheader(title)
    if description:
        st.info(description)
    ph = st.empty()
    ph.write("— data will load from backend API here —")
    return ph
