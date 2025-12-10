import streamlit as st
from pages import api
import pandas as pd

def render(api_url: str):
    st.markdown("""
    <div style="margin-bottom:24px;">
        <h1 style="font-size:32px; font-weight:700; color:#1f2937; margin-bottom:4px;">Campaigns</h1>
        <p style="color:#6b7280; font-size:14px;">Campaign performance pages — hook to `/campaigns` APIs.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Create Campaign")
    with st.form("create_campaign"):
        cols = st.columns(3)
        with cols[0]:
            name = st.text_input("Name", placeholder="Holiday 2025 Campaign")
            brand_options = ["— select brand —"]
            brand_map = {}
            brands_res = api.get('/brands')
            if brands_res:
                if isinstance(brands_res, dict) and 'items' in brands_res:
                    brands = brands_res['items']
                elif isinstance(brands_res, list):
                    brands = brands_res
                else:
                    brands = []
                # keep only Pepsi if present, otherwise first brand
                filtered = [b for b in brands if (b.get('name') or '').lower().startswith('pepsi')]
                if not filtered and brands:
                    filtered = [brands[0]]
                for b in filtered:
                    bid = b.get('brand_id') or b.get('id')
                    bname = b.get('name', f"Brand {bid}")
                    if bid:
                        option = f"{bname} (id:{bid})"
                        brand_options.append(option)
                        brand_map[option] = bid
            brand_choice = st.selectbox("Brand", brand_options)
        with cols[1]:
            objective = st.selectbox("Objective", ["Brand Awareness", "Conversions", "Engagement", "Traffic"])
            status = st.selectbox("Status", ["active", "planned", "paused", "completed"])
        with cols[2]:
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            budget = st.number_input("Budget (USD)", min_value=0.0, value=10000.0, step=1000.0)
        submitted = st.form_submit_button("Create Campaign")
        if submitted:
            errors = []
            if not name.strip():
                errors.append("Name is required.")
            selected_brand_id = brand_map.get(brand_choice) if brand_choice in brand_map else None
            if not selected_brand_id:
                errors.append("Select a brand.")
            if end_date < start_date:
                errors.append("End date cannot be before start date.")
            if errors:
                for e in errors:
                    st.error(e)
            else:
                # Avoid duplicate-name errors by adding a short suffix
                import uuid
                final_name = f"{name.strip()}-{uuid.uuid4().hex[:6]}"

                # Sanitize budget (handle commas)
                safe_budget = 0.0
                try:
                    safe_budget = float(str(budget).replace(',', ''))
                except Exception:
                    safe_budget = float(budget) if budget else 0.0

                payload = {
                    "brand_id": selected_brand_id,
                    "name": final_name,
                    "objective": objective,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "budget": int(safe_budget),
                    "status": status,
                }
                res = api.post('/campaigns', payload)
                if res:
                    st.success(f"Campaign '{payload['name']}' created.")
                    # Clear cache for campaigns endpoint to show new campaign
                    try:
                        from pages.api import _cached_get
                        _cached_get.clear()
                    except:
                        pass  # Cache clear is best-effort
                    st.rerun()
                else:
                    st.error("Failed to create campaign. Check inputs and try again.")
                    st.caption("Tip: Try another name/brand or adjust dates; ensure budget is numeric.")

    st.markdown("---")

    campaigns = []
    # Fetch ALL campaigns first (not just active) to show newly created ones
    res = api.get('/campaigns')
    if isinstance(res, dict) and 'items' in res:
        campaigns = res['items']
    elif isinstance(res, list):
        campaigns = res
    # If no campaigns, try active only
    if not campaigns:
        res = api.get('/campaigns', params={'status':'active'})
        if isinstance(res, dict) and 'items' in res:
            campaigns = res['items']
        elif isinstance(res, list):
            campaigns = res
    # Safely build options list - show ALL campaigns (not limited to 3)
    options = ["— none —"]
    for c in campaigns:
        if isinstance(c, dict):
            name = c.get('name', 'Unknown')
            cid = c.get('campaign_id') or c.get('id', '?')
            options.append(f"{name} (id:{cid})")
        else:
            options.append(f"Campaign {c}")
    selected_campaign = st.selectbox("Select campaign", options)
    if selected_campaign == "— none —":
        st.info("Select a campaign to view detailed metrics.")
    else:
        try:
            cid = int(selected_campaign.split('id:')[-1].strip(')'))
        except Exception:
            cid = None
        
        if cid:
            # Campaign Summary
            st.subheader("Campaign Summary")
            summary = api.get(f'/campaigns/{cid}/summary')
            if summary:
                if isinstance(summary, dict):
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Budget", f"${summary.get('budget', 0):,.2f}" if summary.get('budget') else "—")
                    col2.metric("Influencers", f"{summary.get('influencer_count', 0)}" if summary.get('influencer_count') is not None else "—")
                    col3.metric("Avg Engagement", f"{summary.get('avg_engagement_rate', 0):.2%}" if summary.get('avg_engagement_rate') is not None else "—")
                    col4.metric("Avg Views", f"{summary.get('avg_views', 0):,.0f}" if summary.get('avg_views') is not None else "—")
                    st.caption(f"Status: {summary.get('status', 'Unknown')}")
                else:
                    st.dataframe(pd.DataFrame([summary]))
            else:
                st.info("No summary available.")
            
            # Influencer Performance Table
            st.subheader("Linked Influencers & Content")
            perf = api.get(f'/campaigns/{cid}/influencer-performance')
            if perf and len(perf) > 0:
                try:
                    # Display with influencer names (now included in API response)
                    perf_list = []
                    for row in perf:
                        perf_list.append({
                            'Influencer ID': row.get('influencer_id'),
                            'Influencer Name': row.get('influencer_name', f'Influencer {row.get("influencer_id")}'),
                            'Content ID': row.get('content_id'),
                            'Platform': row.get('platform', 'N/A'),
                            'Role': row.get('role', 'N/A'),
                            'Paid': 'Yes' if row.get('is_paid') else 'No',
                            'Engagement Rate': f"{row.get('engagement_rate', 0):.4f}" if row.get('engagement_rate') else 'N/A',
                            'Likes': row.get('likes', 0) if row.get('likes') else 0,
                            'Comments': row.get('comments', 0) if row.get('comments') else 0,
                            'Views': row.get('views', 0) if row.get('views') else 0,
                        })
                    df = pd.DataFrame(perf_list)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f'Error displaying influencer performance: {e}')
                    # Fallback to formatted display
                    if isinstance(perf, list):
                        st.dataframe(pd.DataFrame(perf))
                    elif isinstance(perf, dict):
                        st.dataframe(pd.DataFrame([perf]))
                    else:
                        st.write(f"Performance data: {perf}")
            else:
                st.info("No influencers/content linked to this campaign yet. Hire influencers from the Recommendations page.")
