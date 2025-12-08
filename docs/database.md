# Database Documentation

PostgreSQL database schema and management for Predictfluence.

## Access

- **Host**: localhost
- **Port**: 5433 (mapped from container port 5432)
- **Database**: predictfluence (from `.env` `DB_NAME`)
- **pgAdmin**: http://localhost:5050

## Schema Overview

The database follows a star schema design with fact and dimension tables.

### Dimension Tables

#### `influencers`
Core influencer information.

**Columns:**
- `influencer_id` (PK): Unique identifier
- `name`: Influencer name
- `username`: Social media username
- `platform`: Platform (Instagram, TikTok, YouTube)
- `follower_count`: Current follower count
- `category`: Content category
- `created_at`: Timestamp

#### `content`
Content posts by influencers.

**Columns:**
- `content_id` (PK): Unique identifier
- `influencer_id` (FK): Reference to influencers
- `content_type`: Type (Image, Video, Reel, Story)
- `topic`: Content topic
- `post_date`: Post date
- `post_datetime`: Post datetime (with time)
- `caption`: Post caption text
- `url`: Content URL

#### `engagement`
Engagement metrics for content.

**Columns:**
- `engagement_id` (PK): Unique identifier
- `content_id` (FK): Reference to content
- `likes`: Number of likes
- `comments`: Number of comments
- `shares`: Number of shares
- `views`: Number of views
- `engagement_rate`: Calculated engagement rate

#### `audience_demographics`
Audience demographic data.

**Columns:**
- `audience_id` (PK): Unique identifier
- `influencer_id` (FK): Reference to influencers
- `age_group`: Age group (18-24, 25-34, etc.)
- `gender`: Gender (Male, Female, Other)
- `country`: Country code
- `percentage`: Percentage of audience

#### `brands`
Brand information.

**Columns:**
- `brand_id` (PK): Unique identifier
- `name`: Brand name
- `industry`: Industry sector
- `country`: Brand country
- `created_at`: Timestamp

#### `campaigns`
Marketing campaigns.

**Columns:**
- `campaign_id` (PK): Unique identifier
- `brand_id` (FK): Reference to brands
- `name`: Campaign name
- `objective`: Campaign objective
- `start_date`: Start date
- `end_date`: End date
- `budget`: Campaign budget
- `status`: Status (active, completed, draft)
- `created_at`: Timestamp

#### `campaign_content`
Links content to campaigns.

**Columns:**
- `id` (PK): Unique identifier
- `campaign_id` (FK): Reference to campaigns
- `content_id` (FK): Reference to content
- `role`: Role (primary, supporting)
- `is_paid`: Whether content is paid

#### `users`
User accounts.

**Columns:**
- `user_id` (PK): Unique identifier
- `email`: User email (unique)
- `hashed_password`: Password hash
- `role`: User role
- `company`: Company name
- `full_name`: Full name
- `created_at`: Timestamp

### Fact Tables

#### `fact_influencer_performance`
Aggregated influencer performance metrics.

**Columns:**
- `id` (PK): Unique identifier
- `influencer_id` (FK): Reference to influencers
- `avg_engagement_rate`: Average engagement rate
- `avg_likes`: Average likes
- `avg_comments`: Average comments
- `avg_shares`: Average shares
- `avg_views`: Average views
- `follower_count`: Current follower count
- `category`: Influencer category
- `audience_top_country`: Top audience country

#### `fact_content_features`
Content features for ML models.

**Columns:**
- `id` (PK): Unique identifier
- `content_id` (FK): Reference to content
- `influencer_id` (FK): Reference to influencers
- `tag_count`: Number of tags (# and @)
- `caption_length`: Caption character length
- `content_type`: Content type
- `engagement_rate`: Engagement rate

### Logging Tables

#### `prediction_logs`
ML prediction history.

**Columns:**
- `log_id` (PK): Unique identifier
- `timestamp`: Prediction timestamp
- `content_id` (FK): Reference to content
- `influencer_id` (FK): Reference to influencers
- `predicted_engagement`: Predicted engagement rate
- `model_version`: Model version used

#### `api_logs`
API call logging.

**Columns:**
- `log_id` (PK): Unique identifier
- `user`: User email
- `endpoint`: API endpoint
- `status`: HTTP status code
- `timestamp`: Request timestamp

## ERD

See `docs/imgs/Project_ERD.pdf` for complete entity-relationship diagram.

## Database Management

### Access via pgAdmin

1. Open http://localhost:5050
2. Login with credentials from `.env`
3. Add server:
   - Host: `postgresql_db` (or `db` in Docker network)
   - Port: `5432`
   - Database: `predictfluence`
   - Username/Password: From `.env`

### Access via psql

```bash
# From host
psql -h localhost -p 5433 -U postgres -d predictfluence

# From container
docker compose exec db psql -U postgres -d predictfluence
```

### Schema Creation

Tables are automatically created on service startup via SQLAlchemy:
- API service: `create_tables()` on startup
- ETL service: Drops and recreates tables before loading data

### Data Loading

Data is loaded via ETL service:
1. Reads CSV files from `Predictfluence/etl/data/`
2. Generates data if CSVs don't exist
3. Populates all tables
4. Calculates fact table aggregations

### Backup & Restore

**Backup:**
```bash
docker compose exec db pg_dump -U postgres predictfluence > backup.sql
```

**Restore:**
```bash
docker compose exec -T db psql -U postgres predictfluence < backup.sql
```

## Indexes

Recommended indexes for production:
- `influencers.platform`
- `influencers.category`
- `content.influencer_id`
- `content.post_date`
- `engagement.content_id`
- `fact_influencer_performance.influencer_id`
- `fact_content_features.influencer_id`

## Data Quality

### Validation Rules
- Follower count > 0
- Engagement rate between 0 and 1
- Dates in valid format
- Required fields not null

### ETL Data Quality Checks
- Validates fact table record counts
- Checks joinability between fact tables
- Verifies required fields are populated

## Performance Optimization

### Query Optimization
- Use fact tables for aggregations
- Join on indexed foreign keys
- Limit result sets with pagination

### Maintenance
- Regular VACUUM and ANALYZE
- Monitor query performance
- Add indexes based on query patterns

---

For ETL process details, see [ETL Documentation](etl.md)

