# Predictfluence API Specification (Milestone 3)

This document lists the required REST endpoints to support the Streamlit UI, backend integrations, and DS service. Base URL defaults to `http://localhost:8000` (or `API_URL` env in the app). All responses are JSON. Timestamps are ISO 8601. Use pagination via `?page` and `?page_size` where noted.

## Auth / User
- `POST /auth/login` → `{ "access_token": "...", "token_type": "bearer", "user": { "email": "...", "role": "PM|Admin|..." } }`
- `GET /user/profile` → current user profile (email, role, company, full_name)
- `PUT /user/profile` body: `{ "full_name": "...", "role": "...", "company": "...", "email": "..." }` → updated profile

## Influencers
- `GET /influencers`
  - Query: `platform`, `category`, `min_followers`, `max_followers`, `country`, `q` (search name/username), `page`, `page_size`
  - Response: `{ "items": [Influencer], "total": 123 }`
- `GET /influencers/{id}` → influencer + optional aggregates; query `include=performance,audience`
- `POST /influencers` body matches `InfluencerCreate`
- `PUT /influencers/{id}` body matches `InfluencerCreate`
- `DELETE /influencers/{id}` → `{ "message": "deleted" }`
- `GET /influencers/{id}/audience` → `[AudienceDemographics]`
- `GET /influencers/{id}/content` → list of content with engagement; filters `content_type`, `start_date`, `end_date`
- `GET /influencers/count` → `{ "count": 120 }` (Dashboard KPI)

### Influencer model
```json
{
  "influencer_id": 1,
  "name": "Jane Doe",
  "username": "jdoe",
  "platform": "Instagram",
  "follower_count": 54000,
  "category": "Beauty",
  "created_at": "2024-11-19T12:00:00Z"
}
```

## Content & Engagement
- `POST /content` body: `{ "influencer_id": 1, "content_type": "Video", "topic": "Beauty", "post_date": "2024-10-10", "caption": "...", "url": "..." }`
- `GET /content/{id}` → content + engagement + campaign links
- `POST /content/{id}/engagement` body: `{ "likes": 1200, "comments": 80, "shares": 30, "views": 15000, "engagement_rate": 0.09 }`
- `GET /content/{id}/engagement` → engagement record

## Brands & Campaigns
- `GET /brands` / `POST /brands` / `GET /brands/{id}`
- `GET /campaigns`
  - Query: `brand_id`, `status`, `start_date`, `end_date`, `page`, `page_size`
  - Response: `{ "items": [Campaign], "total": n }`
- `POST /campaigns` body matches `CampaignCreate`
- `GET /campaigns/{id}` → campaign with brand and linked content ids
- `PUT /campaigns/{id}` / `DELETE /campaigns/{id}`
- `GET /campaigns/{id}/summary`
  - Returns: `{ "campaign_id": 1, "name": "...", "budget": 12000, "status": "active", "spend_to_date": 4300, "influencer_count": 6, "avg_engagement_rate": 0.072, "avg_views": 15000, "avg_cost_per_influencer": 716.67 }`
- `GET /campaigns/{id}/influencer-performance`
  - Table of content/influencer rows with fields: `influencer_id`, `content_id`, `platform`, `engagement_rate`, `likes`, `comments`, `views`, `role`, `is_paid`
- `POST /campaigns/{id}/content`
  - Body: `{ "content_id": 10, "role": "primary|supporting", "is_paid": true }` → links content to campaign

### Campaign model
```json
{
  "campaign_id": 4,
  "brand_id": 2,
  "name": "Holiday Push",
  "objective": "Engagement",
  "start_date": "2024-11-01",
  "end_date": "2024-12-15",
  "budget": 25000,
  "status": "active",
  "created_at": "2024-11-02T10:00:00Z"
}
```

## Analytics (uses fact tables)
- `GET /analytics/engagement?range=30d`
  - Response example: `{ "series": [ { "date": "2024-10-20", "engagement_rate": 0.061 }, ... ] }`
- `GET /analytics/top-campaigns?limit=5&metric=engagement`
  - Returns list of campaigns with metric value and ranking
- `GET /analytics/audience?group_by=country`
  - Aggregates audience_demographics; `group_by` in `country|age_group|gender`
- `GET /analytics/creative`
  - Returns engagement by `content_type`/topic for Insights tab
- `GET /analytics/performance`
  - Overall KPIs: `{ "avg_engagement_rate": 0.065, "avg_likes": 1200, "avg_comments": 80, "avg_views": 15000 }`

## Recommendations / ML
- `POST /recommendations`
  - Body: `{ "platform": "Instagram", "audience_size_band": "10k-100k", "category": "Beauty", "country": "USA", "content_type": "Video" }`
  - Response: list of suggested influencers/content with rationale and predicted engagement
- `POST /ml/train` (proxy to DS `/train`)
  - Response: `{ "n_rows": 300, "used_synthetic": true, "r2": 0.72, "mae": 0.015, "model_version": "baseline-20241119120000", "features": ["follower_count","tag_count","caption_length","content_type"] }`
- `POST /ml/predict` (proxy to DS `/predict`)
  - Body: `{ "follower_count": 120000, "tag_count": 3, "caption_length": 140, "content_type": "Video", "content_id": 10, "influencer_id": 2 }`
  - Response: `{ "predicted_engagement_rate": 0.083, "model_version": "baseline-...", "logged": true }`

## Health / Logs
- `GET /health` → `{ "status": "ok", "db": "connected" }`
- `GET /logs/api` (admin) → recent API log entries with `user`, `endpoint`, `status`, `timestamp`

## Error format
Use FastAPI default or standardized: `{ "detail": "message" }` with proper HTTP status codes (400 validation, 401 auth, 404 not found, 500 server).
