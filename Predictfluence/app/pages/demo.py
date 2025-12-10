import streamlit as st


def render(api_url: str):
    st.markdown("""
    <style>
    .demo-hero {
        text-align: center;
        padding: 48px 24px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 24px;
        margin-bottom: 48px;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.3);
    }
    .demo-hero h1 {
        font-size: 48px;
        font-weight: 800;
        color: #ffffff;
        margin: 0 0 12px 0;
        letter-spacing: -0.5px;
    }
    .demo-hero p {
        font-size: 20px;
        color: rgba(255, 255, 255, 0.95);
        margin: 0;
        font-weight: 400;
    }
    .problem-solution-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 32px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
        height: 100%;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .problem-solution-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
    .problem-solution-card h3 {
        font-size: 24px;
        font-weight: 700;
        color: #1f2937;
        margin: 0 0 16px 0;
        padding-bottom: 16px;
        border-bottom: 2px solid #f3f4f6;
    }
    .problem-card h3 {
        border-bottom-color: #fee2e2;
        color: #dc2626;
    }
    .solution-card h3 {
        border-bottom-color: #dbeafe;
        color: #2563eb;
    }
    .outcome-card h3 {
        border-bottom-color: #d1fae5;
        color: #059669;
    }
    .problem-solution-card ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    .problem-solution-card li {
        padding: 12px 0;
        font-size: 15px;
        color: #4b5563;
        line-height: 1.6;
        border-bottom: 1px solid #f3f4f6;
    }
    .problem-solution-card li:last-child {
        border-bottom: none;
    }
    .problem-solution-card li:before {
        content: "•";
        color: #9ca3af;
        font-weight: bold;
        display: inline-block;
        width: 20px;
        margin-left: -20px;
    }
    .checklist-section {
        background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
        border-radius: 20px;
        padding: 40px;
        margin: 48px 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    }
    .checklist-section h2 {
        font-size: 28px;
        font-weight: 700;
        color: #1f2937;
        margin: 0 0 24px 0;
        text-align: center;
    }
    .checklist-item {
        display: flex;
        align-items: center;
        padding: 16px 20px;
        margin: 12px 0;
        background: #ffffff;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        font-size: 16px;
        color: #1f2937;
        font-weight: 500;
        transition: all 0.2s;
    }
    .checklist-item:hover {
        background: #f9fafb;
        border-color: #d1d5db;
        transform: translateX(4px);
    }
    .checklist-check {
        width: 24px;
        height: 24px;
        border-radius: 6px;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin-right: 16px;
        flex-shrink: 0;
    }
    .checklist-check::after {
        content: "✓";
        color: white;
        font-weight: bold;
        font-size: 14px;
    }
    .reassurance-section {
        background: #f0f9ff;
        border-left: 4px solid #2563eb;
        border-radius: 12px;
        padding: 24px 32px;
        margin: 48px 0 24px 0;
    }
    .reassurance-section p {
        font-size: 16px;
        color: #1e40af;
        margin: 8px 0;
        line-height: 1.6;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div class="demo-hero">
        <h1>Predictfluence</h1>
        <p>Data-driven influencer recommendations for real campaign ROI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Problem / Solution / Outcome Section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="problem-solution-card problem-card">
            <h3>Problem</h3>
            <p style="font-size: 18px; font-weight: 600; color: #dc2626; margin-bottom: 20px;">
                Picking the right influencers and proving ROI is hard.
            </p>
            <ul>
                <li>Too many influencers, not enough signal</li>
                <li>Decisions made from gut feeling and screenshots</li>
                <li>Hard to connect content performance back to campaign spend</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="problem-solution-card solution-card">
            <h3>Solution</h3>
            <p style="font-size: 18px; font-weight: 600; color: #2563eb; margin-bottom: 20px;">
                Predictfluence combines your campaign data, influencer performance, and ML predictions.
            </p>
            <ul>
                <li>Centralized campaigns + influencers</li>
                <li>ML-powered recommendations for each campaign</li>
                <li>Live performance tracking and insights</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="problem-solution-card outcome-card">
            <h3>Outcome</h3>
            <p style="font-size: 18px; font-weight: 600; color: #059669; margin-bottom: 20px;">
                Faster sourcing, better fit, clearer ROI.
            </p>
            <ul>
                <li>Shortlist best-fit influencers</li>
                <li>Track campaign engagement & cost per influencer</li>
                <li>Learn what audience & content actually work</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # What I'll show you today section
    st.markdown("""
    <div class="checklist-section">
        <h2>What I'll show you today</h2>
        <div class="checklist-item">
            <span class="checklist-check"></span>
            <span><strong>Dashboard:</strong> health of all campaigns & influencers</span>
        </div>
        <div class="checklist-item">
            <span class="checklist-check"></span>
            <span><strong>Campaigns:</strong> create a campaign, see its performance</span>
        </div>
        <div class="checklist-item">
            <span class="checklist-check"></span>
            <span><strong>Recommendations:</strong> get ML-based influencer suggestions & hire</span>
        </div>
        <div class="checklist-item">
            <span class="checklist-check"></span>
            <span><strong>Influencers:</strong> deep dive into creator performance</span>
        </div>
        <div class="checklist-item">
            <span class="checklist-check"></span>
            <span><strong>Insights:</strong> audience & creative learnings for next campaigns</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Reassurance section
    st.markdown("""
    <div class="reassurance-section">
        <p>Recommendations are powered by machine learning, not manual guesswork.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
    <div style="text-align: center; margin-top: 32px; padding: 24px; background: #ffffff; border-radius: 16px; border: 1px solid #e5e7eb;">
        <p style="font-size: 18px; color: #4b5563; margin: 0;">
            Ready to explore? Use the sidebar to navigate to <strong>Dashboard</strong> and start the demo.
        </p>
    </div>
    """, unsafe_allow_html=True)
