# Predictfluence - Micro-Influencer Analytics Platform

A comprehensive analytics platform for discovering, evaluating, and managing micro-influencer marketing campaigns with AI-powered recommendations.

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- `.env` file configured (see `.env.example`)

### Run the Application

```bash
# Start all services
docker compose up --build

# Or run in detached mode
docker compose up -d --build
```

### Access the Services

Once running, access the services at:

- **Streamlit Frontend**: http://localhost:8501
- **FastAPI Backend**: http://localhost:8008
- **API Documentation (Swagger)**: http://localhost:8008/docs
- **API Documentation (ReDoc)**: http://localhost:8008/redoc
- **Data Science Service**: http://localhost:8010
- **DS Service Documentation**: http://localhost:8010/docs
- **pgAdmin**: http://localhost:5050
  - Email: (from `.env` `PGADMIN_EMAIL`)
  - Password: (from `.env` `PGADMIN_PASSWORD`)
- **PostgreSQL Database**: `localhost:5432`

### Documentation

- **MkDocs Documentation**: See `docs/` folder
- **API Documentation**: http://localhost:8008/docs (Swagger UI)
- **Project Documentation**: See `PROJECT_DOCUMENTATION.md`

## Project Overview

Predictfluence is an analytics platform that helps marketing managers:

- **Discover** micro-influencers across platforms (Instagram, TikTok, YouTube)
- **Evaluate** influencer performance using ML-powered predictions
- **Manage** marketing campaigns and track ROI
- **Analyze** audience demographics and engagement trends
- **Get Recommendations** for optimal influencer partnerships

## Architecture

The platform consists of 6 main services:

1. **Database (PostgreSQL)**: Stores all data including influencers, campaigns, content, and analytics
2. **ETL Service**: Extracts, transforms, and loads data from CSV files into the database
3. **API Service (FastAPI)**: RESTful API providing all backend endpoints
4. **Data Science Service (FastAPI)**: ML models for engagement prediction, tier classification, clustering, and scheduling
5. **Frontend (Streamlit)**: Interactive web application for users
6. **pgAdmin**: Database administration interface

## Project Structure

```
group-4/
├── docker-compose.yml          # Docker orchestration
├── .env                        # Environment variables (create from .env.example)
├── README.md                   # This file
├── PROJECT_DOCUMENTATION.md    # Comprehensive project documentation
├── mkdocs.yaml                 # MkDocs configuration
├── docs/                       # Documentation source files
│   ├── index.md
│   ├── problem_definition.md
│   ├── api.md
│   ├── app.md
│   └── etl.md
└── Predictfluence/
    ├── api/                    # FastAPI backend service
    ├── app/                    # Streamlit frontend
    ├── ds/                     # Data science service
    ├── etl/                    # ETL service
    └── postgres_data/          # PostgreSQL data (auto-generated)
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory with:

```env
# Database
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=predictfluence
DATABASE_URL=postgresql+psycopg2://postgres:your_password@db:5432/predictfluence

# pgAdmin
PGADMIN_EMAIL=admin@example.com
PGADMIN_PASSWORD=admin_password

# Services
DS_URL=http://ds:8010
API_URL=http://api:8000
```

## Features

### Dashboard
- Real-time KPIs (Active Campaigns, Total Influencers, Avg Engagement, Avg Cost)
- Engagement trends over time
- Top-performing campaigns

### Influencers
- Browse and filter influencers by platform, category, follower count
- View detailed profiles with performance metrics
- Audience demographics analysis
- Content history

### Campaigns
- Create and manage marketing campaigns
- Track campaign performance
- Link content to campaigns
- View influencer performance within campaigns

### Recommendations
- AI-powered influencer recommendations
- Filter by platform, audience size, content type, category
- Predicted engagement rates
- Influencer tier classification (Elite/Professional/Emerging)

### Insights
- Audience analytics (demographics by country, age, gender)
- Creative performance (engagement by content type)
- Advanced ML insights (skill scores, clustering, posting schedules)

## Machine Learning Models

The platform includes several ML models:

1. **Engagement Rate Predictor**: Gradient Boosting Regressor predicting engagement rates
2. **Tier Classifier**: Categorizes influencers as Elite/Professional/Emerging
3. **Influencer Clustering**: K-Means clustering for influencer segmentation
4. **Posting Schedule Optimizer**: Time-aware analysis for optimal posting times

Models auto-train on startup if sufficient data is available (≥40 rows).

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `GET /user/profile` - Get user profile
- `PUT /user/profile` - Update user profile

### Influencers
- `GET /influencers` - List influencers (with filters)
- `GET /influencers/count` - Get total influencer count
- `GET /influencers/{id}` - Get influencer details
- `POST /influencers` - Create influencer
- `PUT /influencers/{id}` - Update influencer
- `DELETE /influencers/{id}` - Delete influencer
- `GET /influencers/{id}/audience` - Get audience demographics
- `GET /influencers/{id}/content` - Get influencer content

### Campaigns
- `GET /campaigns` - List campaigns
- `POST /campaigns` - Create campaign
- `GET /campaigns/{id}` - Get campaign details
- `PUT /campaigns/{id}` - Update campaign
- `DELETE /campaigns/{id}` - Delete campaign
- `GET /campaigns/{id}/summary` - Get campaign summary
- `GET /campaigns/{id}/influencer-performance` - Get influencer performance
- `POST /campaigns/{id}/content` - Link content to campaign

### Analytics
- `GET /analytics/engagement` - Engagement trends over time
- `GET /analytics/top-campaigns` - Top performing campaigns
- `GET /analytics/audience` - Audience demographics analysis
- `GET /analytics/creative` - Creative performance by type
- `GET /analytics/performance` - Overall performance KPIs

### ML/Recommendations
- `POST /recommendations` - Get AI-powered recommendations
- `POST /ml/predict` - Predict engagement rate
- `POST /ml/train` - Train ML model
- `POST /ml/insights/skill-scores` - Get influencer skill scores
- `POST /ml/insights/tier/predict` - Predict influencer tier
- `POST /ml/insights/clusters` - Get influencer clusters
- `GET /ml/insights/posting-schedule` - Get optimal posting schedule
- `POST /ml/batch-score` - Batch scoring for multiple influencers

### Health & Logs
- `GET /health` - Service health check
- `GET /logs/api` - API call logs

**Full API Documentation**: http://localhost:8008/docs (Swagger UI)

## Development

### Running Locally (without Docker)

```bash
# Install dependencies
cd Predictfluence/api && pip install -r requirements.txt
cd ../app && pip install -r requirements.txt
cd ../ds && pip install -r requirements.txt
cd ../etl && pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql+psycopg2://postgres:password@localhost:5433/predictfluence"

# Run services
# Terminal 1: API
cd Predictfluence/api && uvicorn main:app --reload --port 8000

# Terminal 2: DS Service
cd Predictfluence/ds && uvicorn main:app --reload --port 8010

# Terminal 3: Streamlit
cd Predictfluence/app && streamlit run app.py
```

### Database Migrations

The database schema is managed via SQLAlchemy models. Tables are auto-created on service startup. To reset:

```bash
# Stop containers
docker compose down

# Remove database data (WARNING: deletes all data)
rm -rf Predictfluence/postgres_data

# Restart
docker compose up --build
```

## Screenshots

### Dashboard
![Dashboard 1](docs/imgs/dashboard1.png)
![Dashboard 2](docs/imgs/dashboard2.png)

### Influencers
![Influencers 1](docs/imgs/influencers1.png)
![Influencers 2](docs/imgs/influencers2.png)

### Campaigns
![Campaigns 1](docs/imgs/campaigns1.png)
![Campaigns 2](docs/imgs/campaigns2.png)

### Recommendations
![Recommendations](docs/imgs/recommendations.png)

### Insights
![Insights 1](docs/imgs/insights1.png)
![Insights 2](docs/imgs/insights2.png)

## Cleanup

To stop and remove all containers:

```bash
docker compose down
```

To also remove volumes (database data):

```bash
docker compose down -v
```

## Additional Documentation

- **Project Documentation**: See `PROJECT_DOCUMENTATION.md` for detailed explanations
- **MkDocs**: Run `mkdocs serve` to view documentation locally
- **API Docs**: Interactive Swagger UI at http://localhost:8008/docs
- **Database Schema**: See `docs/imgs/Project_ERD.pdf`

## Troubleshooting

### Port Already in Use
If ports are already in use, modify `docker-compose.yml` to use different ports.

### Database Connection Errors
- Ensure PostgreSQL container is healthy: `docker compose ps`
- Check `.env` file has correct `DATABASE_URL`
- Verify database credentials

### ETL Not Running
- Check ETL container logs: `docker compose logs etl`
- Ensure CSV files exist in `Predictfluence/etl/data/`
- ETL auto-generates data if CSVs don't exist

### ML Models Not Training
- Check DS service logs: `docker compose logs ds`
- Ensure database has ≥40 rows of data
- Models will use synthetic data as fallback

## Team

- **Product Manager**: Hamlet Brutyan
- **Backend Developer**: Elena Melkonyan
- **Frontend Developer**: Mane Poghosyan
- **Data Scientist**: Serine Poghosyan
- **Database Developer**: Tatev Stepanyan

## License

This project is part of DS-223-2025-Fall course.

## Links

- **Streamlit App**: http://localhost:8501
- **API Swagger**: http://localhost:8008/docs
- **API ReDoc**: http://localhost:8008/redoc
- **DS Service Docs**: http://localhost:8010/docs
- **pgAdmin**: http://localhost:5050
- **MkDocs**: Run `mkdocs serve` (default: http://localhost:8000)

---

**Status**: Production Ready

All services are fully integrated and functional. The platform is ready for deployment and use.

