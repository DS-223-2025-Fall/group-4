import streamlit as st
from pages.components import placeholder_section
from pages import api

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

        submitted = st.form_submit_button("Save Changes")

        if submitted:
            payload = {
                'full_name': full_name,
                'email': email,
                'role': role if role!='Select Role' else None,
                'company': company
            }
            if st.session_state.get('demo_mode'):
                st.success('Saved (demo)')
            else:
                res = api.put('/user/profile', payload)
                if res is not None:
                    st.success('Profile updated')
                else:
                    st.error('Failed to save profile')

    placeholder_section(
        "Update Profile Placeholder",
        f"Would call PUT {api_url}/user/profile with the provided fields."
    )
