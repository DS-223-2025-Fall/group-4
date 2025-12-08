# Predictfluence - Project Documentation

## Project Overview

Predictfluence is a micro-influencer analytics platform that helps marketing managers discover, evaluate, and manage influencer marketing campaigns using AI-powered predictions and data-driven insights.

## Architecture

The platform consists of six main services orchestrated via Docker Compose:

1. **PostgreSQL Database**: Stores all data including influencers, campaigns, content, and analytics
2. **ETL Service**: Extracts, transforms, and loads data from CSV files into the database
3. **FastAPI Backend**: RESTful API providing all backend endpoints
4. **Data Science Service**: ML models for engagement prediction, tier classification, clustering, and scheduling
5. **Streamlit Frontend**: Interactive web application for users
6. **pgAdmin**: Database administration interface

## Technology Stack

- **Frontend**: Streamlit (Python)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ML Framework**: scikit-learn (Gradient Boosting)
- **Containerization**: Docker & Docker Compose
- **Documentation**: MkDocs with Material theme

## Core Features

### 1. Influencer Discovery
- Browse influencers by platform (Instagram, TikTok, YouTube), category, and follower count
- Search by name or username
- View detailed profiles with performance metrics
- Audience demographics analysis

### 2. Campaign Management
- Create and manage marketing campaigns
- Link influencers and content to campaigns
- Track campaign performance in real-time
- Budget tracking and cost analysis

### 3. AI-Powered Recommendations
- ML-based engagement rate predictions
- Influencer tier classification (Elite/Professional/Emerging)
- Filtered recommendations based on platform, audience size, content type, and category

### 4. Advanced Analytics
- Engagement trends over time
- Top-performing campaigns
- Audience demographics breakdown (by country, age group, gender)
- Creative performance by content type
- Influencer skill scores
- Optimal posting schedule suggestions

### 5. Machine Learning Models

#### Engagement Rate Predictor
- **Algorithm**: Gradient Boosting Regressor
- **Features**: follower_count, tag_count, caption_length, content_type, category, audience_top_country
- **Output**: Predicted engagement rate (0-1)
- **Auto-training**: Trains on startup if database has ≥40 rows

#### Tier Classifier
- **Algorithm**: Gradient Boosting Classifier
- **Output**: Elite/Professional/Emerging classification
- **Purpose**: Categorizes influencers based on performance

#### Influencer Clustering
- **Algorithm**: K-Means
- **Output**: Cluster assignments with characteristics
- **Purpose**: Groups similar influencers for segmentation

#### Posting Schedule Optimizer
- **Method**: Time-series analysis
- **Output**: Optimal posting days and hours
- **Purpose**: Suggests best times to post based on historical engagement

## Database Schema

The database follows a star schema design:

### Dimension Tables
- `influencers`: Core influencer information
- `content`: Content posts with captions and metadata
- `engagement`: Engagement metrics
- `audience_demographics`: Demographic breakdowns
- `brands`: Brand information
- `campaigns`: Campaign details
- `campaign_content`: Campaign-content associations
- `users`: User accounts

### Fact Tables
- `fact_influencer_performance`: Aggregated influencer metrics
- `fact_content_features`: Content features for ML models

### Logging Tables
- `prediction_logs`: ML prediction history
- `api_logs`: API call logging

## API Endpoints

The platform provides 44+ REST API endpoints:

- **Authentication**: Login, user profile management
- **Influencers**: CRUD operations, audience data, content history
- **Campaigns**: Campaign management, performance tracking
- **Analytics**: Engagement trends, top campaigns, audience demographics, creative performance
- **ML/Recommendations**: Predictions, training, skill scores, clustering, posting schedules
- **Health & Logs**: Service health checks, API logging

Full API documentation available at: http://localhost:8008/docs

## Frontend Pages

### Dashboard
High-level KPIs and charts showing overall campaign performance.

### Influencers
Browse, filter, and search influencers with detailed profile views.

### Campaigns
Manage campaigns and view influencer performance within campaigns.

### Recommendations
AI-powered influencer recommendations with predicted engagement rates.

### Insights
Advanced analytics including audience demographics and creative performance.

### Settings
User profile management.

## Data Flow

1. **ETL Service** loads data from CSV files into PostgreSQL
2. **Database** stores all structured data
3. **API Service** exposes data via REST endpoints
4. **DS Service** provides ML predictions and analytics
5. **Streamlit App** consumes API endpoints to display data and visualizations

## Deployment

The platform is fully containerized using Docker Compose:

```bash
docker compose up --build
```

All services start automatically with proper dependencies and health checks.

## Development

### Local Development
Each service can run independently:
- API: `uvicorn main:app --reload`
- DS: `uvicorn main:app --reload --port 8010`
- App: `streamlit run app.py`

### Environment Variables
Configured via `.env` file:
- Database credentials
- Service URLs
- pgAdmin credentials

## Documentation

- **README.md**: Quick start guide and overview
- **docs/**: MkDocs documentation
  - API Service documentation
  - Streamlit App documentation
  - Data Science Service documentation
  - ETL Service documentation
  - Database documentation
- **Swagger UI**: Interactive API documentation at http://localhost:8008/docs

## Team

- **Product Manager**: Hamlet Brutyan
- **Backend Developer**: Elena Melkonyan
- **Frontend Developer**: Mane Poghosyan
- **Data Scientist**: Serine Poghosyan
- **Database Developer**: Tatev Stepanyan

## Project Status

**Status**: Production Ready

All services are fully integrated and functional. The platform is ready for deployment and use.

---

For detailed service documentation, see the `docs/` folder or visit http://localhost:8008/docs for interactive API documentation.
