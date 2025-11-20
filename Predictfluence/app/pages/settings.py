# pages/settings.py
# pages/settings.py

import streamlit as st
from pages.components import placeholder_section


def render(api_url: str):
    st.title("Settings / Profile")

    st.markdown("Manage your account information. All fields currently use placeholders until the API is connected.")

    with st.form("profile_form"):
        st.subheader("Profile Information")

        full_name = st.text_input("Full Name", placeholder="Enter your full name")

        email = st.text_input(
            "Email Address",
            placeholder="Enter your email"
        )

        role = st.selectbox(
            "Role",
            [
                "Select Role",
                "Marketing Manager",
                "Campaign Analyst",
                "Brand Manager",
                "Data Scientist",
                "Influencer Manager",
                "Admin",
            ],
        )

        company = st.text_input(
            "Company",
            placeholder="Enter your company name"
        )

        st.form_submit_button("Save Changes")

    placeholder_section(
        "Update Profile Placeholder",
        f"Would call PUT {api_url}/user/profile with the provided fields."
    )
