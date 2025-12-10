import streamlit as st
import pandas as pd
from pages.components import placeholder_section
from pages import api

def render(api_url: str):
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="font-size:32px; font-weight:700; color:#1f2937; margin-bottom:4px;">Recommendations</h1>
        <p style="color:#6b7280; font-size:14px;">ML-powered influencer recommendations based on engagement predictions.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show success message if hire was successful
    if 'hire_success' in st.session_state:
        success = st.session_state['hire_success']
        st.success(f"Successfully hired {success['influencer_name']} for {success['campaign_name']}!")
        st.balloons()
        st.info(f"""
        **Hire Summary:**
        - **Influencer:** {success['influencer_name']} (@{success.get('username', 'N/A')})
        - **Campaign:** {success['campaign_name']}
        - **Role:** {success['role']}
        - **Type:** {'Paid' if success['is_paid'] else 'Unpaid'} Collaboration
        """)
        # Clear success message after showing
        del st.session_state['hire_success']

    st.subheader("Filters")

    cols = st.columns(4)

    with cols[0]:
        platform = st.multiselect(
            "Platform(s)",
            ["Instagram", "TikTok", "YouTube", "Facebook", "All"],
            default=["Instagram"]
        )

    with cols[1]:
        audience = st.selectbox(
            "Audience Size",
            ["Any", "1k–10k", "10k–100k", "100k–500k", "500k+"]
        )

    with cols[2]:
        category = st.multiselect(
            "Category",
            ["Beauty", "Fashion", "Lifestyle", "Tech", "Gaming", "Travel", "Food", "Fitness", "Finance", "Music", "Any"],
            default=["Beauty"]
        )

    with cols[3]:
        content_type = st.multiselect(
            "Preferred Content Type",
            ["Video", "Reel/Shorts", "Story", "Image/Carousel", "Live", "Any"],
            default=["Video"]
        )

    run = st.button("Get Recommendations", type="primary")

    # Store recommendations in session state when fetched
    if run:
        # Map filters to payload
        platform_val = None
        if platform:
            cleaned = [p for p in platform if p != "All"]
            if cleaned:
                platform_val = cleaned[0]  # API expects a single string

        category_val = None
        if category:
            cleaned = [c for c in category if c != "Any"]
            if cleaned:
                category_val = cleaned[0]  # API expects a single string

        content_val = None
        if content_type:
            cleaned = [c for c in content_type if c != "Any"]
            if cleaned:
                content_val = cleaned[0]  # API expects a single string

        audience_map = {
            '1k–10k': 'micro',
            '10k–100k': 'mid',
            '100k–500k': 'macro',
            '500k+': 'mega'
        }
        audience_size_band = audience_map.get(audience) if audience != 'Any' else None

        payload = {
            'platform': platform_val,
            'category': category_val,
            'content_type': content_val,
            'audience_size_band': audience_size_band
        }
        payload = {k: v for k, v in payload.items() if v not in [None, [], ""]}
        
        with st.spinner("Fetching recommendations..."):
            res = api.post('/recommendations', payload)
        
        if res and isinstance(res, dict) and 'recommendations' in res:
            recommendations_list = res['recommendations']
            if recommendations_list:
                # Store in session state so it persists
                st.session_state.recommendations_list = recommendations_list
                st.session_state.selected_reco_id = None  # Clear any previous selection
            else:
                st.info("No recommendations found matching your criteria.")
                st.session_state.recommendations_list = []
        elif res:
            st.warning(f"Unexpected response format: {res}")
            st.session_state.recommendations_list = []
        else:
            st.error(f"Failed to get recommendations. Please check your connection and try again.")
            st.session_state.recommendations_list = []

    # Display stored recommendations
    recommendations_list = st.session_state.get('recommendations_list', [])
    
    if recommendations_list:
        st.subheader("Suggested Influencers")
        
        # Display recommendations in a grid
        num_cols = min(3, len(recommendations_list))
        cols = st.columns(num_cols)
        
        for idx, (col, result) in enumerate(zip(cols, recommendations_list)):
            with col:
                # Card styling
                st.markdown("""
                <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 16px; margin-bottom: 16px; background-color: #ffffff;">
                """, unsafe_allow_html=True)
                
                # Influencer name
                st.markdown(f"### {result.get('influencer_name', 'Unknown')}")
                
                # Platform badge
                if result.get('platform'):
                    st.markdown(f"**Platform:** {result['platform']}")
                
                # Predicted engagement
                if 'predicted_engagement' in result:
                    engagement_val = result['predicted_engagement']
                    st.metric(
                        "Predicted Engagement",
                        f"{engagement_val:.2%}",
                        help="ML-predicted engagement rate for this influencer"
                    )
                
                # Rationale
                if 'rationale' in result:
                    st.caption(result['rationale'])
                
                # Action buttons
                if 'influencer_id' in result:
                    inf_id = result['influencer_id']
                    btn_col1, btn_col2 = st.columns(2)
                    
                    with btn_col1:
                        if st.button("View Details", key=f"view_{inf_id}", use_container_width=True):
                            st.session_state.selected_reco_id = inf_id
                            st.session_state[f"hire_mode_{inf_id}"] = False
                            st.rerun()
                    
                    with btn_col2:
                        if st.button("Hire", key=f"hire_quick_{inf_id}", use_container_width=True, type="primary"):
                            st.session_state.selected_reco_id = inf_id
                            st.session_state[f"hire_mode_{inf_id}"] = True
                            st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)

    # Show selected recommendation detail if set
    selected_id = st.session_state.get("selected_reco_id")
    if selected_id:
        st.markdown("---")
        
        with st.spinner("Loading influencer details..."):
            detail = api.get(f'/influencers/{selected_id}', params={'include': 'performance,audience'})
            # Also fetch performance and audience separately if not in detail
            if detail and not detail.get('performance'):
                perf = api.get(f'/influencers/{selected_id}/performance')
                if perf:
                    detail['performance'] = perf
            if detail and not detail.get('audience'):
                aud = api.get(f'/influencers/{selected_id}/audience')
                if aud:
                    # Convert list to dict format
                    aud_dict = {}
                    for item in aud:
                        if isinstance(item, dict):
                            if 'country' in item:
                                if 'country' not in aud_dict:
                                    aud_dict['country'] = {}
                                aud_dict['country'][item['country']] = item.get('percentage', 0)
                    if aud_dict:
                        detail['audience'] = aud_dict
        
        if detail:
            st.markdown("### Influencer Details")
            name = detail.get('name') or detail.get('influencer', {}).get('name') or "Unknown"
            platform = detail.get('platform') or detail.get('influencer', {}).get('platform')
            username = detail.get('username') or detail.get('influencer', {}).get('username')
            follower_count = detail.get('follower_count') or detail.get('influencer', {}).get('follower_count', 0)
            
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.markdown(f"**Name:** {name}")
                st.markdown(f"**Username:** {username or 'N/A'}")
            with col_info2:
                st.markdown(f"**Platform:** {platform or 'Platform N/A'}")
                st.markdown(f"**Followers:** {follower_count:,}" if follower_count else "**Followers:** N/A")

            perf = detail.get('performance')
            if perf and isinstance(perf, dict):
                st.markdown("#### Performance Metrics")
                colp1, colp2, colp3 = st.columns(3)
                colp1.metric("Avg Engagement Rate", f"{perf.get('avg_engagement_rate', 0):.2%}" if perf.get('avg_engagement_rate') is not None else "—")
                colp2.metric("Avg Likes", f"{perf.get('avg_likes', 0):,.0f}" if perf.get('avg_likes') is not None else "—")
                colp3.metric("Avg Views", f"{perf.get('avg_views', 0):,.0f}" if perf.get('avg_views') is not None else "—")

            aud = detail.get('audience')
            if aud:
                st.markdown("#### Audience Demographics")
                # API returns list of AudienceDemographics objects
                if isinstance(aud, list) and len(aud) > 0:
                    # Group by country, age_group, or gender
                    country_data = {}
                    age_data = {}
                    gender_data = {}
                    for item in aud:
                        if isinstance(item, dict):
                            if item.get('country'):
                                country_data[item['country']] = float(item.get('percentage', 0))
                            elif item.get('age_group'):
                                age_data[item['age_group']] = float(item.get('percentage', 0))
                            elif item.get('gender'):
                                gender_data[item['gender']] = float(item.get('percentage', 0))
                    
                    if country_data:
                        df_aud = pd.DataFrame(list(country_data.items()), columns=['country', 'percentage']).set_index('country')
                        st.bar_chart(df_aud)
                        st.caption("Top countries by audience share.")
                    elif age_data:
                        df_aud = pd.DataFrame(list(age_data.items()), columns=['age_group', 'percentage']).set_index('age_group')
                        st.bar_chart(df_aud)
                        st.caption("Audience distribution by age.")
                    elif gender_data:
                        df_aud = pd.DataFrame(list(gender_data.items()), columns=['gender', 'percentage']).set_index('gender')
                        st.bar_chart(df_aud)
                        st.caption("Audience distribution by gender.")
                elif isinstance(aud, dict):
                    # Fallback for dict format
                    if 'country' in aud and isinstance(aud['country'], dict):
                        df_aud = pd.DataFrame(list(aud['country'].items()), columns=['country', 'percentage']).set_index('country')
                        st.bar_chart(df_aud)
                        st.caption("Top countries by audience share.")

            # Check if we're in "hire" mode
            hire_mode = st.session_state.get(f"hire_mode_{selected_id}", False)
            
            # Action buttons
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("Back to Recommendations", key=f"back_{selected_id}"):
                    st.session_state.selected_reco_id = None
                    st.session_state[f"hire_mode_{selected_id}"] = False
                    st.rerun()
            
            with col2:
                if not hire_mode:
                    if st.button("Hire This Influencer", key=f"hire_btn_{selected_id}", type="primary", use_container_width=True):
                        st.session_state[f"hire_mode_{selected_id}"] = True
                        st.rerun()
            
            # Show hire section if in hire mode
            if hire_mode:
                st.markdown("---")
                st.markdown("### Hire Influencer for Campaign")
                
                # Fetch all campaigns (active first, then all)
                campaigns = []
                with st.spinner("Loading campaigns..."):
                    res = api.get('/campaigns', params={'status': 'active'})
                    if isinstance(res, dict) and 'items' in res:
                        campaigns = res['items']
                    elif isinstance(res, list):
                        campaigns = res
                    
                    # If no active campaigns, get all campaigns
                    if not campaigns:
                        res = api.get('/campaigns')
                        if isinstance(res, dict) and 'items' in res:
                            campaigns = res['items']
                        elif isinstance(res, list):
                            campaigns = res
                
                if not campaigns:
                    st.warning("No campaigns available. Please create a campaign first.")
                else:
                    # Build campaign options
                    options = ["— Select a campaign —"]
                    c_map = {}
                    campaign_info = {}
                    
                    for c in campaigns:
                        cid = c.get('campaign_id') or c.get('id')
                        cname = c.get('name', f"Campaign {cid}")
                        status = c.get('status', 'unknown')
                        budget = c.get('budget', 0)
                        if cid:
                            # Show status and budget in the label
                            status_indicator = "[ACTIVE]" if status == "active" else "[PLANNED]" if status == "planned" else "[OTHER]"
                            label = f"{status_indicator} {cname} ({status})"
                            options.append(label)
                            c_map[label] = cid
                            campaign_info[cid] = {
                                'name': cname,
                                'status': status,
                                'budget': budget
                            }
                    
                    selected_campaign = st.selectbox(
                        "Select Campaign",
                        options,
                        key=f"campaign_select_{selected_id}"
                    )
                    
                    if selected_campaign and selected_campaign != "— Select a campaign —":
                        cid = c_map.get(selected_campaign)
                        if cid:
                            # Show campaign info
                            campaign = campaign_info.get(cid, {})
                            st.info(f"**Campaign:** {campaign.get('name', 'Unknown')} | **Status:** {campaign.get('status', 'Unknown')} | **Budget:** ${campaign.get('budget', 0):,.2f}")
                            
                            # Role and payment options
                            col_role, col_paid = st.columns(2)
                            with col_role:
                                role = st.selectbox(
                                    "Role",
                                    ["primary", "supporting", "testimonial"],
                                    key=f"role_{selected_id}",
                                    help="Primary: Main influencer, Supporting: Secondary, Testimonial: Review/testimonial content"
                                )
                            
                            with col_paid:
                                is_paid = st.checkbox(
                                    "Paid Collaboration",
                                    value=True,
                                    key=f"paid_{selected_id}",
                                    help="Check if this is a paid partnership. Paid collaborations involve monetary compensation to the influencer for creating and sharing content about your brand."
                                )
                            
                            # Confirm hire button
                            st.markdown("---")
                            col_confirm, col_cancel = st.columns([2, 1])
                            
                            with col_confirm:
                                if st.button(
                                    f"Confirm Hire for {campaign.get('name', 'Campaign')}",
                                    key=f"confirm_hire_{selected_id}",
                                    type="primary",
                                    use_container_width=True
                                ):
                                    # Make API call to hire (content_id will be auto-selected by API if not provided)
                                    payload = {
                                        "influencer_id": int(selected_id),
                                        "role": role,
                                        "is_paid": is_paid
                                    }
                                    
                                    with st.spinner("Hiring influencer..."):
                                        res_attach = api.post(f'/campaigns/{cid}/content', payload)
                                    
                                    if res_attach is not None:
                                        # Store success message in session state
                                        st.session_state['hire_success'] = {
                                            'influencer_name': name,
                                            'campaign_name': campaign.get('name', 'Unknown'),
                                            'role': role.title(),
                                            'is_paid': is_paid,
                                            'username': username
                                        }
                                        
                                        # Clear API cache to refresh campaign data
                                        try:
                                            from pages.api import _cached_get
                                            _cached_get.clear()
                                        except:
                                            pass
                                        
                                        # Clear states and reset
                                        st.session_state.selected_reco_id = None
                                        st.session_state[f"hire_mode_{selected_id}"] = False
                                        
                                        st.rerun()
                                    else:
                                        st.error("Failed to hire influencer. Please check the campaign and try again.")
                            
                            with col_cancel:
                                if st.button(
                                    "Cancel",
                                    key=f"cancel_hire_{selected_id}",
                                    use_container_width=True
                                ):
                                    st.session_state[f"hire_mode_{selected_id}"] = False
                                    st.rerun()
        else:
            st.error("Could not load influencer details from API.")
            if st.button("Back to Recommendations"):
                st.session_state.selected_reco_id = None
                st.rerun()
