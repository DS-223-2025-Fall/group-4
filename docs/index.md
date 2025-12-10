# Predictfluence - Micro-Influencer Analytics Platform

## Problem

Marketing managers struggle to identify and evaluate micro-influencers for their campaigns. Traditional methods are time-consuming, lack data-driven insights, and don't scale well. There's a need for:

- **Efficient Discovery**: Quickly find relevant influencers across platforms
- **Performance Prediction**: Understand potential engagement before campaign launch
- **ROI Tracking**: Measure campaign effectiveness and costs
- **Data-Driven Decisions**: Make informed choices based on analytics, not guesswork

## Solution

Predictfluence is a comprehensive analytics platform that combines:

1. **Database-Driven Analytics**: Centralized data warehouse with fact tables for performance metrics
2. **Machine Learning Models**: AI-powered engagement prediction, tier classification, and clustering
3. **Interactive Dashboard**: Streamlit-based UI for easy exploration and management
4. **RESTful API**: Production-ready backend with comprehensive endpoints
5. **Automated ETL**: Data pipeline that populates the database from CSV sources

## Expected Outcomes

### For Marketing Managers

- **Time Savings**: Reduce influencer discovery time by 80%
- **Better ROI**: Make data-driven decisions leading to 20-30% better campaign performance
- **Scalability**: Manage hundreds of influencers and campaigns from one platform
- **Predictive Insights**: Know engagement rates before committing to partnerships

### For Organizations

- **Centralized Data**: Single source of truth for all influencer and campaign data
- **Historical Analysis**: Track performance trends over time
- **Audience Insights**: Understand demographics and preferences
- **Cost Optimization**: Track and optimize spending per influencer

### Technical Outcomes

- **Production-Ready Stack**: Fully containerized, scalable architecture
- **ML Integration**: Real-time predictions with auto-retraining
- **API-First Design**: Easy integration with other tools
- **Comprehensive Documentation**: Complete API docs, user guides, and technical documentation

## Key Features

### 1. Influencer Discovery & Evaluation
- Browse influencers by platform, category, follower count
- View all influencers (up to 200 per page)
- View detailed profiles with performance metrics (Avg Engagement Rate, Avg Likes, Avg Views)
- Table and Card view modes for easy browsing

### 2. Campaign Management
- Create and manage marketing campaigns
- Hire influencers directly from Recommendations page
- Track campaign performance with summary metrics (Budget, Influencer Count, Avg Engagement, Avg Views)
- View linked influencer performance within campaigns

### 3. AI-Powered Recommendations
- ML-based engagement rate predictions
- Filter by platform, audience size, content type, and category
- View influencer details and hire directly to campaigns
- Predicted engagement rates with rationale for each recommendation

### 4. Advanced Analytics
- Engagement trends over time (last 30 days)
- Top-performing campaigns by engagement rate
- Audience demographics breakdown (by country, age group, gender)
- Creative performance by content type
- Dashboard KPIs: Total Campaigns, Total Influencers, Avg Engagement Rate, Avg Cost per Influencer

### 5. Production-Ready Infrastructure
- Docker containerization for easy deployment
- PostgreSQL database with optimized schema
- FastAPI backend with Swagger documentation
- Streamlit frontend with responsive design
- Automated ETL pipeline

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Streamlit  │────▶│   FastAPI   │────▶│ PostgreSQL  │
│   Frontend  │     │    API      │     │  Database   │
└─────────────┘     └─────────────┘     └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │  DS Service │
                    │  (ML Models)│
                    └─────────────┘
                            │
                            ▼
                    ┌─────────────┐
                    │  ETL Service│
                    │  (Data Load)│
                    └─────────────┘
```

## Technology Stack

- **Frontend**: Streamlit (Python)
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ML Framework**: scikit-learn (Gradient Boosting)
- **Containerization**: Docker & Docker Compose
- **Documentation**: MkDocs with Material theme

## Getting Started

See the [README](../README.md) for quick start instructions.

## Documentation Structure

- **[Problem Definition](problem_definition.md)**: Detailed problem analysis
- **[API Documentation](api.md)**: Complete API endpoint reference
- **[Application Guide](app.md)**: Frontend features and usage
- **[ETL Documentation](etl.md)**: Data pipeline and ETL process

## Next Steps

1. **Deploy**: Follow deployment instructions in README
2. **Explore**: Use the Streamlit app to discover features
3. **Integrate**: Use the API to integrate with other tools
4. **Extend**: Build custom analytics using the ML models

---

**Built by the Predictfluence Team**
