# Streamlit UI ↔ API Mapping

This guide helps frontend/PM see how each Streamlit page connects to the planned API endpoints and which components to use.

## Global
- Config: `API_URL` env (already in `app.py`). Centralize fetch helpers with `requests` and `st.cache_data`.
- Common UI: `st.spinner` around API calls; show `st.error` on failures.

## Login page (`pages/login.py`)
- Endpoints: `POST /auth/login` (optional demo fallback).
- Components: `st.text_input`, `st.button`. On success set session auth token for downstream requests.

## Dashboard (`pages/dashboard.py`)
- KPIs:  
  - Active campaigns → `GET /campaigns?status=active` (count) or `GET /campaigns/summary`.
  - Total influencers → `GET /influencers/count`.
  - Avg engagement → `GET /analytics/performance` (field `avg_engagement_rate`).
  - Avg cost/influencer → `GET /campaigns/{id}/summary` aggregated or `GET /analytics/performance` (extend to include cost).
- Charts:  
  - Engagement over time → `GET /analytics/engagement?range=30d`; render with `st.altair_chart` or `plotly.express.line`.
  - Top campaigns → `GET /analytics/top-campaigns?limit=5`; use bar chart/table.

## Influencers (`pages/influencers.py`)
- Directory/table → `GET /influencers` with filters (platform, category, follower range, q). Render via `st.dataframe`/`st.data_editor`.
- Detail modal/link → `GET /influencers/{id}` with `include=performance,audience`.
- Audience breakdown → `GET /influencers/{id}/audience` (charts: pie/bar).
- Content list → `GET /influencers/{id}/content` (use columns/cards; optional `st.image`/`st.video`).

## Campaigns (`pages/campaigns.py`)
- List dropdown → `GET /campaigns?status=active` (or all); show name/id.
- Summary panel → `GET /campaigns/{id}/summary`.
- Influencer performance table → `GET /campaigns/{id}/influencer-performance` (table with role, paid flag, metrics).
- Attach content (future form) → `POST /campaigns/{id}/content`.

## Recommendations (`pages/recommendations.py`)
- Filters → match payload for `POST /recommendations`.
- Results grid → display returned influencers/content with predicted engagement and rationale; optionally include CTA to view influencer detail.
- Optionally trigger `POST /ml/predict` per card to refresh scores.

## Insights (`pages/insights.py`)
- Audience tab → `GET /analytics/audience?group_by=country|age_group|gender`; use bar/treemap.
- Creative tab → `GET /analytics/creative`; show engagement by content type/topic (bar or heatmap).

## Settings (`pages/settings.py`)
- Load profile → `GET /user/profile`.
- Save profile → `PUT /user/profile`.

## Components to consider
- Tables/grids: `st.dataframe`, `st.data_editor`, or `st-aggrid` for richer controls.
- Charts: `st.altair_chart`, `plotly.express` for interactive hover/zoom.
- Filters: `st.multiselect`, `st.slider` (follower range), `st.date_input`, `st.segmented_control`.
- Layout: `st.columns` for KPI cards, `st.tabs` (already used), `st.expander` for advanced filters.
