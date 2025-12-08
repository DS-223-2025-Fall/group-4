# API Documentation

Complete REST API reference for Predictfluence backend service.

**Base URL**: `http://localhost:8008` (or `API_URL` environment variable)  
**Interactive Docs**: http://localhost:8008/docs (Swagger UI)  
**Alternative Docs**: http://localhost:8008/redoc (ReDoc)

All responses are JSON. Timestamps use ISO 8601 format.

---

## Authentication & User Management

### `POST /auth/login`
User authentication.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "full_name": "John Doe",
  "role": "Marketing Manager",
  "company": "Acme Corp"
}
```

**Response:**
```json
{
  "access_token": "demo-token-user@example.com",
  "token_type": "bearer",
  "user": {
    "email": "user@example.com",
    "role": "Marketing Manager",
    "company": "Acme Corp",
    "full_name": "John Doe"
  }
}
```

### `GET /user/profile`
Get current user profile.

**Query Parameters:**
- `email` (optional): Filter by email

**Response:**
```json
{
  "email": "user@example.com",
  "role": "Marketing Manager",
  "company": "Acme Corp",
  "full_name": "John Doe"
}
```

### `PUT /user/profile`
Update user profile.

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "full_name": "Jane Doe",
  "role": "Admin",
  "company": "New Corp"
}
```

**Response:** Updated user profile (same format as GET)

---

## Influencers

### `GET /influencers`
List influencers with filters and pagination.

**Query Parameters:**
- `platform` (optional): Filter by platform (Instagram, TikTok, YouTube)
- `category` (optional): Filter by category
- `min_followers` (optional): Minimum follower count
- `max_followers` (optional): Maximum follower count
- `country` (optional): Filter by audience top country
- `q` (optional): Search by name or username
- `page` (default: 1): Page number
- `page_size` (default: 20, max: 200): Items per page

**Response:**
```json
{
  "items": [
    {
      "influencer_id": 1,
      "name": "Jane Doe",
      "username": "jdoe",
      "platform": "Instagram",
      "follower_count": 54000,
      "category": "Beauty",
      "created_at": "2024-11-19T12:00:00Z"
    }
  ],
  "total": 150
}
```

### `GET /influencers/count`
Get total influencer count (for dashboard KPI).

**Response:**
```json
{
  "count": 150
}
```

### `GET /influencers/{influencer_id}`
Get influencer details with optional performance and audience data.

**Query Parameters:**
- `include` (optional): Comma-separated list: `performance`, `audience`

**Response:**
```json
{
  "influencer": {
    "influencer_id": 1,
    "name": "Jane Doe",
    "username": "jdoe",
    "platform": "Instagram",
    "follower_count": 54000,
    "category": "Beauty",
    "created_at": "2024-11-19T12:00:00Z"
  },
  "performance": {
    "influencer_id": 1,
    "avg_engagement_rate": 0.065,
    "avg_likes": 1200,
    "follower_count": 54000,
    "category": "Beauty",
    "audience_top_country": "USA"
  },
  "audience": [
    {
      "audience_id": 1,
      "influencer_id": 1,
      "age_group": "18-24",
      "gender": "Female",
      "country": "USA",
      "percentage": 45.5
    }
  ]
}
```

### `POST /influencers`
Create a new influencer.

**Request Body:**
```json
{
  "name": "John Smith",
  "username": "jsmith",
  "platform": "TikTok",
  "follower_count": 25000,
  "category": "Gaming"
}
```

**Response:** Created influencer object

### `PUT /influencers/{influencer_id}`
Update an influencer.

**Request Body:** Same as POST

**Response:** Updated influencer object

### `DELETE /influencers/{influencer_id}`
Delete an influencer.

**Response:**
```json
{
  "message": "deleted"
}
```

### `GET /influencers/{influencer_id}/audience`
Get audience demographics for an influencer.

**Response:**
```json
[
  {
    "audience_id": 1,
    "influencer_id": 1,
    "age_group": "18-24",
    "gender": "Female",
    "country": "USA",
    "percentage": 45.5
  }
]
```

### `GET /influencers/{influencer_id}/content`
Get content list for an influencer.

**Query Parameters:**
- `content_type` (optional): Filter by content type
- `start_date` (optional): Filter by start date
- `end_date` (optional): Filter by end date

**Response:** Array of content objects

---

## Content & Engagement

### `POST /content`
Create a content record.

**Request Body:**
```json
{
  "influencer_id": 1,
  "content_type": "Video",
  "topic": "Beauty",
  "post_date": "2024-10-10",
  "caption": "Check out this amazing product!",
  "url": "https://example.com/post/123"
}
```

**Response:** Created content object

### `GET /content/{content_id}`
Get content details with engagement and campaign links.

**Response:**
```json
{
  "content": {
    "content_id": 1,
    "influencer_id": 1,
    "content_type": "Video",
    "topic": "Beauty",
    "post_date": "2024-10-10",
    "caption": "...",
    "url": "...",
    "post_datetime": "2024-10-10T12:00:00Z"
  },
  "engagement": {
    "engagement_id": 1,
    "content_id": 1,
    "likes": 1200,
    "comments": 80,
    "shares": 30,
    "views": 15000,
    "engagement_rate": 0.09
  },
  "campaigns": [1, 2]
}
```

### `POST /content/{content_id}/engagement`
Create or update engagement metrics.

**Request Body:**
```json
{
  "likes": 1200,
  "comments": 80,
  "shares": 30,
  "views": 15000,
  "engagement_rate": 0.09
}
```

**Response:** Engagement object

### `GET /content/{content_id}/engagement`
Get engagement metrics for content.

**Response:** Engagement object

---

## Brands & Campaigns

### `GET /brands`
List all brands.

**Response:** Array of brand objects

### `POST /brands`
Create a brand.

**Request Body:**
```json
{
  "name": "Acme Corp",
  "industry": "Fashion",
  "country": "USA"
}
```

**Response:** Created brand object

### `GET /brands/{brand_id}`
Get brand details.

**Response:** Brand object

### `GET /campaigns`
List campaigns with filters.

**Query Parameters:**
- `brand_id` (optional): Filter by brand
- `status` (optional): Filter by status (active, completed, draft)
- `start_date` (optional): Filter by start date
- `end_date` (optional): Filter by end date
- `page` (default: 1): Page number
- `page_size` (default: 20): Items per page

**Response:**
```json
{
  "items": [
    {
      "campaign_id": 1,
      "brand_id": 1,
      "name": "Holiday Push",
      "objective": "Engagement",
      "start_date": "2024-11-01",
      "end_date": "2024-12-15",
      "budget": 25000,
      "status": "active",
      "created_at": "2024-11-02T10:00:00Z"
    }
  ],
  "total": 40
}
```

### `POST /campaigns`
Create a campaign.

**Request Body:**
```json
{
  "brand_id": 1,
  "name": "Holiday Push",
  "objective": "Engagement",
  "start_date": "2024-11-01",
  "end_date": "2024-12-15",
  "budget": 25000,
  "status": "active"
}
```

**Response:** Created campaign object

### `GET /campaigns/{campaign_id}`
Get campaign details.

**Response:**
```json
{
  "campaign": {
    "campaign_id": 1,
    "brand_id": 1,
    "name": "Holiday Push",
    "objective": "Engagement",
    "start_date": "2024-11-01",
    "end_date": "2024-12-15",
    "budget": 25000,
    "status": "active",
    "created_at": "2024-11-02T10:00:00Z"
  },
  "brand": {
    "brand_id": 1,
    "name": "Acme Corp",
    "industry": "Fashion",
    "country": "USA"
  },
  "content_links": [
    {
      "id": 1,
      "campaign_id": 1,
      "content_id": 10,
      "role": "primary",
      "is_paid": true
    }
  ]
}
```

### `PUT /campaigns/{campaign_id}`
Update a campaign.

**Request Body:** Same as POST

**Response:** Updated campaign object

### `DELETE /campaigns/{campaign_id}`
Delete a campaign.

**Response:**
```json
{
  "message": "deleted"
}
```

### `GET /campaigns/{campaign_id}/summary`
Get campaign performance summary.

**Response:**
```json
{
  "campaign_id": 1,
  "name": "Holiday Push",
  "budget": 25000,
  "status": "active",
  "spend_to_date": 4300,
  "influencer_count": 6,
  "avg_engagement_rate": 0.072,
  "avg_views": 15000,
  "avg_cost_per_influencer": 716.67
}
```

### `GET /campaigns/{campaign_id}/influencer-performance`
Get influencer performance data for a campaign.

**Response:**
```json
[
  {
    "influencer_id": 1,
    "content_id": 10,
    "platform": "Instagram",
    "engagement_rate": 0.045,
    "likes": 1200,
    "comments": 80,
    "views": 15000,
    "role": "primary",
    "is_paid": true
  }
]
```

### `POST /campaigns/{campaign_id}/content`
Link content to a campaign.

**Request Body:**
```json
{
  "content_id": 10,
  "role": "primary",
  "is_paid": true
}
```

**Response:**
```json
{
  "message": "linked"
}
```

---

## Analytics

### `GET /analytics/engagement`
Get engagement trends over time.

**Query Parameters:**
- `range` (optional): Time range (e.g., "30d", "7d", "90d")

**Response:**
```json
{
  "series": [
    {
      "date": "2024-10-20",
      "engagement_rate": 0.061
    },
    {
      "date": "2024-10-21",
      "engagement_rate": 0.065
    }
  ]
}
```

### `GET /analytics/top-campaigns`
Get top performing campaigns.

**Query Parameters:**
- `limit` (default: 5, max: 50): Number of campaigns to return
- `metric` (default: "engagement"): Metric to rank by (engagement or views)

**Response:**
```json
{
  "items": [
    {
      "campaign_id": 1,
      "name": "Holiday Push",
      "metric_value": 0.072,
      "rank": 1
    }
  ]
}
```

### `GET /analytics/audience`
Get audience demographics aggregated by dimension.

**Query Parameters:**
- `group_by` (default: "country"): Group by country, age_group, or gender

**Response:**
```json
{
  "group_by": "country",
  "items": [
    {
      "group": "USA",
      "percentage": 45.5
    },
    {
      "group": "UK",
      "percentage": 22.3
    }
  ]
}
```

### `GET /analytics/creative`
Get creative performance by content type.

**Response:**
```json
{
  "items": [
    {
      "content_type": "Video",
      "topic": "Beauty",
      "avg_engagement_rate": 0.065
    },
    {
      "content_type": "Image",
      "topic": "Fashion",
      "avg_engagement_rate": 0.052
    }
  ]
}
```

### `GET /analytics/performance`
Get overall performance KPIs.

**Response:**
```json
{
  "avg_engagement_rate": 0.065,
  "avg_likes": 1200,
  "avg_comments": 80,
  "avg_views": 15000,
  "avg_cost_per_influencer": 716.67
}
```

---

## Recommendations & ML

### `POST /recommendations`
Get AI-powered influencer recommendations.

**Request Body:**
```json
{
  "platform": "Instagram",
  "audience_size_band": "10k-100k",
  "category": "Beauty",
  "country": "USA",
  "content_type": "Video"
}
```

**Response:**
```json
{
  "recommendations": [
    {
      "influencer_id": 1,
      "influencer_name": "Jane Doe",
      "platform": "Instagram",
      "predicted_engagement": 0.083,
      "rationale": "Platform: Instagram; Category: Beauty; ML-predicted engagement rate",
      "content_id": null
    }
  ]
}
```

### `POST /ml/train`
Trigger ML model training (proxies to DS service).

**Response:**
```json
{
  "n_rows": 300,
  "used_synthetic": false,
  "r2": 0.72,
  "mae": 0.015,
  "model_version": "model-20241208120538",
  "features": ["follower_count", "tag_count", "caption_length", "content_type", "category", "audience_top_country"]
}
```

### `POST /ml/predict`
Predict engagement rate for content (proxies to DS service).

**Request Body:**
```json
{
  "follower_count": 120000,
  "tag_count": 3,
  "caption_length": 140,
  "content_type": "Video",
  "content_id": 10,
  "influencer_id": 2
}
```

**Response:**
```json
{
  "predicted_engagement_rate": 0.083,
  "model_version": "model-20241208120538",
  "logged": true
}
```

### `POST /ml/insights/skill-scores`
Get influencer skill scores based on model residuals.

**Response:**
```json
{
  "scores": [
    {
      "influencer_id": 1,
      "n_posts": 25,
      "mean_residual": 0.012,
      "skill_score": 0.010
    }
  ],
  "version": "skill-20241208120538"
}
```

### `POST /ml/insights/tier/predict`
Predict content tier (Elite/Professional/Emerging).

**Request Body:**
```json
{
  "follower_count": 120000,
  "tag_count": 3,
  "caption_length": 140,
  "content_type": "Video"
}
```

**Response:**
```json
{
  "tier": "Elite",
  "confidence": 0.85,
  "model_version": "tier-20241208120538"
}
```

### `POST /ml/insights/tier/train`
Train the tier classifier model.

**Response:**
```json
{
  "n_rows": 300,
  "accuracy": 0.78,
  "f1_score": 0.75,
  "model_version": "tier-20241208120538"
}
```

### `POST /ml/insights/clusters`
Cluster influencers using K-Means.

**Query Parameters:**
- `n_clusters` (default: 5, min: 2, max: 10): Number of clusters

**Response:**
```json
{
  "clusters": [
    {
      "cluster_id": 0,
      "influencer_ids": [1, 5, 12],
      "characteristics": {
        "avg_followers": 50000,
        "avg_engagement": 0.065
      }
    }
  ],
  "n_clusters": 5
}
```

### `GET /ml/insights/posting-schedule`
Get optimal posting schedule based on historical patterns.

**Response:**
```json
{
  "best_days": ["Monday", "Wednesday", "Friday"],
  "best_hours": [14, 18, 20],
  "day_stats": {
    "Monday": 0.065,
    "Tuesday": 0.058
  },
  "hour_stats": {
    "14": 0.072,
    "18": 0.068
  }
}
```

### `POST /ml/batch-score`
Run batch scoring on all available data.

**Response:**
```json
{
  "n_scored": 150,
  "predictions": [
    {
      "influencer_id": 1,
      "content_id": 10,
      "predicted_engagement": 0.083,
      "tier": "Elite"
    }
  ]
}
```

---

## Health & Monitoring

### `GET /health`
Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "db": "connected"
}
```

### `GET /logs/api`
Get API call logs.

**Query Parameters:**
- `limit` (default: 50, max: 500): Number of log entries

**Response:**
```json
{
  "items": [
    {
      "log_id": 1,
      "user": "user@example.com",
      "endpoint": "/influencers",
      "status": "200",
      "timestamp": "2024-12-08T12:00:00Z"
    }
  ],
  "total": 150
}
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `400 Bad Request`: Validation error
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Request validation failed
- `500 Internal Server Error`: Server error
- `502 Bad Gateway`: DS service unavailable
- `503 Service Unavailable`: Service temporarily unavailable

**Error Format:**
```json
{
  "detail": "Error message description"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider adding:
- Request throttling per user/IP
- API key authentication
- Rate limit headers in responses

---

## Authentication

Currently uses a lightweight demo authentication system. For production:
- Implement JWT tokens
- Add token expiration
- Add refresh tokens
- Implement proper password hashing (bcrypt)

---

For interactive API testing, visit: **http://localhost:8008/docs**
