# pages/recommendations.py

import streamlit as st
from pages.components import placeholder_section


def render(api_url: str):
    st.title("Recommendations")
    st.markdown("AI/algorithmic suggestions — placeholder for future `/recommendations` endpoint.")

    st.subheader("Filters")

    cols = st.columns(4)

    with cols[0]:
        st.selectbox(
            "Platform",
            ["All", "Instagram", "TikTok", "YouTube"]
        )

    with cols[1]:
        st.selectbox(
            "Audience Size",
            ["Any", "1k–10k", "10k–100k", "100k+"]
        )

    with cols[2]:
        st.selectbox(
            "Content Type",
            [
                "Any",
                "Lifestyle",
                "Beauty",
                "Fashion",
                "Tech",
                "Gaming",
                "Fitness",
                "Travel",
                "Food",
            ]
        )

    with cols[3]:
        st.button("Run Recommendations")

    placeholder_section(
        "Suggested Influencers",
        f"Results from POST {api_url}/recommendations with selected filters"
    )

