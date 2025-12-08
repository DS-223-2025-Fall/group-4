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
            # Input validation
            errors = []
            if not full_name or len(full_name.strip()) == 0:
                errors.append("Full name is required")
            if not email or len(email.strip()) == 0:
                errors.append("Email is required")
            elif '@' not in email or '.' not in email.split('@')[1]:
                errors.append("Please enter a valid email address")
            if role == 'Select Role':
                errors.append("Please select a role")
            if not company or len(company.strip()) == 0:
                errors.append("Company name is required")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                payload = {
                    'full_name': full_name.strip(),
                    'email': email.strip().lower(),
                    'role': role if role!='Select Role' else None,
                    'company': company.strip()
                }
                if st.session_state.get('demo_mode'):
                    st.success('Saved (demo)')
                else:
                    res = api.put('/user/profile', payload)
                    if res is not None:
                        st.success('Profile updated successfully')
                        st.rerun()  # Reload to show updated data
                    else:
                        st.error('Failed to save profile. Please try again.')
