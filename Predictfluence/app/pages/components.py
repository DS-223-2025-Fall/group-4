import streamlit as st

def inject_styles() -> None:
    """Global theme overrides to mimic the provided InfluenceIQ look."""
    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Poppins:wght@400;600&display=swap" rel="stylesheet">
        <style>
        :root {
          --primary: #15c0e3;
          --primary-dark: #2f80ed;
          --card-bg: #ffffff;
          --muted: #6b7280;
          --soft: #f6f8fb;
        }
        html, body, [data-testid="stApp"] {
          font-family: "Inter","Poppins", sans-serif;
          background: var(--soft);
          color: #1f2937;
        }
        /* Sidebar */
        section[data-testid="stSidebar"] {
          background: #ffffff;
          border-right: 1px solid #eef1f6;
        }
        /* Buttons */
        .stButton button, .stForm button {
          border: none;
          color: #fff;
          border-radius: 12px;
          padding: 0.8rem 1.2rem;
          font-weight: 700;
          background: linear-gradient(90deg,#12c2e9,#0fb9b1,#2f80ed);
          box-shadow: 0 10px 24px rgba(47,128,237,0.18);
        }
        .stButton button:hover {
          filter: brightness(0.97);
          box-shadow: 0 12px 30px rgba(47,128,237,0.24);
        }
        /* Secondary / outline button container */
        .outline-btn button {
          background: transparent !important;
          color: #0f9bd7 !important;
          border: 1px solid #0f9bd7 !important;
          box-shadow: none !important;
        }
        /* Inputs */
        .stTextInput input, .stTextArea textarea, .stNumberInput input {
          border-radius: 14px;
          border: 1px solid #dfe5ef;
          padding: 0.8rem 1rem;
          background: #fff;
        }
        .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
          border-color: #2f80ed;
          box-shadow: 0 0 0 2px rgba(47,128,237,0.12);
        }
        /* Cards */
        .iq-card {
          background: var(--card-bg);
          border-radius: 18px;
          padding: 18px;
          border: 1px solid #eef1f6;
          box-shadow: 0 12px 28px rgba(15,23,42,0.08);
        }
        .iq-kpi {
          background: var(--card-bg);
          border-radius: 16px;
          padding: 16px;
          border: 1px solid #eef1f6;
          box-shadow: 0 8px 20px rgba(15,23,42,0.07);
        }
        .iq-pill {
          display: inline-flex;
          align-items: center;
          padding: 4px 10px;
          border-radius: 999px;
          font-size: 12px;
          font-weight: 600;
          background: #e6f7f8;
          color: #0f9bd7;
        }
        /* Plotly charts container */
        div[data-testid="stPlotlyChart"] {
          background: #fff;
          padding: 14px;
          border-radius: 16px;
          border: 1px solid #eef1f6;
          box-shadow: 0 10px 24px rgba(15,23,42,0.07);
        }
        /* Dataframes */
        .stDataFrame { border-radius: 14px; border: 1px solid #eef1f6; overflow: hidden; }
        /* Login centering */
        .login-wrap {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 85vh;
        }
        .login-card {
          max-width: 460px;
          width: 100%;
          background: #fff;
          border-radius: 22px;
          padding: 28px 32px;
          border: 1px solid #e6ebf2;
          box-shadow: 0 18px 36px rgba(15,23,42,0.12);
        }
        .login-divider {
          display: grid;
          grid-template-columns: 1fr auto 1fr;
          align-items: center;
          gap: 8px;
          color: #9ca3af;
          font-size: 13px;
          margin: 12px 0 6px;
        }
        /* Hide Streamlit's automatic pages navigation - comprehensive */
        section[data-testid="stSidebar"] nav[data-testid="stSidebarNav"],
        section[data-testid="stSidebar"] nav[data-testid="stSidebarNav"] ul,
        section[data-testid="stSidebar"] div[data-testid="stSidebarNav"],
        nav[data-testid="stSidebarNav"],
        div[data-testid="stSidebarNav"],
        /* Hide navigation in header */
        header[data-testid="stHeader"] nav,
        div[data-testid="stHeader"] nav,
        /* Hide any navigation links that Streamlit auto-generates */
        a[data-testid="stAppViewContainer"] nav,
        /* Hide page navigation in main content area */
        div[data-testid="stAppViewContainer"] > nav,
        /* Hide any ul/li navigation lists for pages */
        ul[data-testid="stSidebarNav"] {
          display: none !important;
          visibility: hidden !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(title: str, value: str, subtitle: str = ""):
    card = st.container()
    with card:
        st.markdown(f"""
        <div class="iq-kpi">
          <div style="display:flex; justify-content:space-between; align-items:center; gap:8px">
            <div>
              <div style="font-size:13px; color:#6b7280; margin-bottom:4px;">{title}</div>
              <div style="font-size:24px; font-weight:700; color:#1f2937; margin-bottom:2px;">{value}</div>
              <div style="font-size:12px; color:#9ca3af;">{subtitle}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

def section_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div style="display:flex; align-items:center; justify-content:space-between; margin: 6px 4px 12px;">
          <div>
            <div style="font-size:18px; font-weight:700;">{title}</div>
            <div style="font-size:13px; color:#6b7280;">{subtitle}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def placeholder_section(title: str, description: str = None):
    st.subheader(title)
    # Don't show description/placeholder text - just return empty container
    ph = st.empty()
    return ph
