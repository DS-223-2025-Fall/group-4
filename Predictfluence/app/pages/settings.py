import streamlit as st
from pages.components import placeholder_section
from pages import api

def render(api_url: str):
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="font-size:32px; font-weight:700; color:#1f2937; margin-bottom:4px;">Settings / Profile</h1>
        <p style="color:#6b7280; font-size:14px;">Manage your account information.</p>
    </div>
    """, unsafe_allow_html=True)

    # Load existing profile data
    profile_data = None
    if st.session_state.get('demo_mode'):
        profile_data = {
            'full_name': 'Demo User',
            'email': 'demo@example.com',
            'role': 'Marketing Manager',
            'company': 'Demo Company'
        }
    else:
        profile_data = api.get('/user/profile')
    
    # Default values
    default_name = profile_data.get('full_name', '') if profile_data else ''
    default_email = profile_data.get('email', '') if profile_data else ''
    default_role = profile_data.get('role', 'Select Role') if profile_data else 'Select Role'
    default_company = profile_data.get('company', '') if profile_data else ''

    with st.form("profile_form"):
        st.subheader("Profile Information")

        full_name = st.text_input("Full Name", value=default_name, placeholder="Enter your full name")

        email = st.text_input(
            "Email Address",
            value=default_email,
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
            index=0 if default_role == 'Select Role' or default_role not in [
                "Select Role",
                "Marketing Manager",
                "Campaign Analyst",
                "Brand Manager",
                "Data Scientist",
                "Influencer Manager",
                "Admin",
            ] else [
                "Select Role",
                "Marketing Manager",
                "Campaign Analyst",
                "Brand Manager",
                "Data Scientist",
                "Influencer Manager",
                "Admin",
            ].index(default_role)
        )

        company = st.text_input(
            "Company",
            value=default_company,
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
                    st.experimental_rerun()  # Reload to show updated data
                else:
                    st.error('Failed to save profile')
