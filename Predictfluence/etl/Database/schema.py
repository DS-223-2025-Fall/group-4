"""
Pydantic Schemas for Predictfluence Influencer Marketing Project.

This module defines Pydantic models for data validation and serialization
in API requests and responses. The schemas mirror the SQLAlchemy ORM models
and are used for input validation, API payloads, and response models.

Key Concepts:
- Base classes define common fields shared between Create and Read models.
- `Create` classes define payloads for API input (e.g., POST requests).
- Read/Response classes include database-generated fields (e.g., IDs) and
  enable ORM compatibility via `orm_mode`.
- Optional fields reflect nullable database columns or fields with defaults.

Schemas / Models:
- UserBase / UserCreate / User: Users with hashed passwords and roles.
- InfluencerBase / InfluencerCreate / Influencer: Influencer metadata.
- ContentBase / ContentCreate / Content: Individual posts by influencers.
- EngagementBase / EngagementCreate / Engagement: Engagement metrics per content.
- AudienceDemographicsBase / AudienceDemographicsCreate / AudienceDemographics: Influencer audience breakdown.
- FactInfluencerPerformanceBase / FactInfluencerPerformanceCreate / FactInfluencerPerformance: Aggregated influencer performance.
- FactContentFeaturesBase / FactContentFeaturesCreate / FactContentFeatures: Aggregated content features.
- PredictionLogBase / PredictionLogCreate / PredictionLog: Model prediction logging.
- APILogBase / APILogCreate / APILog: API request logging.
- BrandBase / BrandCreate / Brand: Brands in campaigns.
- CampaignBase / CampaignCreate / Campaign: Campaigns linked to brands.
- CampaignContentBase / CampaignContentCreate / CampaignContent: Links content to campaigns with cost and role info.

Usage:
1. Use `Create` schemas to validate input payloads in FastAPI endpoints.
2. Use response schemas (e.g., `User`, `Influencer`) to serialize ORM objects.
3. Enable `orm_mode = True` in response schemas to work seamlessly with SQLAlchemy ORM objects.

Example:
    from Schemas import UserCreate, User
    from fastapi import FastAPI, Depends
    from sqlalchemy.orm import Session
    from Database.database import get_db

    app = FastAPI()

    @app.post("/users/", response_model=User)
    def create_user(user: UserCreate, db: Session = Depends(get_db)):
        db_user = UserDB(**user.dict())
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


# -----------------------------
# Users
# -----------------------------
class UserBase(BaseModel):
    email: str
    hashed_password: str
    role: Optional[str] = None
    company: Optional[str] = None
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None


class UserCreate(UserBase):
    """Payload for creating a user."""


class User(UserBase):
    user_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Influencers
# -----------------------------
class InfluencerBase(BaseModel):
    name: str
    username: str
    platform: str
    follower_count: int
    category: str
    created_at: Optional[datetime] = None


class InfluencerCreate(InfluencerBase):
    """Payload for creating an influencer."""


class Influencer(InfluencerBase):
    influencer_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Content
# -----------------------------
class ContentBase(BaseModel):
    influencer_id: int
    content_type: str
    topic: Optional[str] = None
    post_date: Optional[date] = None
    post_datetime: Optional[datetime] = None  # For hour-level posting schedule analysis
    caption: Optional[str] = None
    url: Optional[str] = None


class ContentCreate(ContentBase):
    """Payload for creating content."""


class Content(ContentBase):
    content_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Engagement
# -----------------------------
class EngagementBase(BaseModel):
    content_id: int
    likes: Optional[int] = 0
    comments: Optional[int] = 0
    shares: Optional[int] = 0
    views: Optional[int] = 0
    engagement_rate: Optional[float] = 0.0


class EngagementCreate(EngagementBase):
    """Payload for creating engagement records."""


class Engagement(EngagementBase):
    engagement_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Audience Demographics
# -----------------------------
class AudienceDemographicsBase(BaseModel):
    influencer_id: int
    age_group: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    percentage: Optional[float] = 0.0


class AudienceDemographicsCreate(AudienceDemographicsBase):
    """Payload for creating an audience demographic record."""


class AudienceDemographics(AudienceDemographicsBase):
    audience_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Fact Influencer Performance
# -----------------------------
class FactInfluencerPerformanceBase(BaseModel):
    influencer_id: int
    avg_engagement_rate: Optional[float] = 0.0
    avg_likes: Optional[float] = 0.0
    avg_comments: Optional[float] = 0.0
    avg_shares: Optional[float] = 0.0
    avg_views: Optional[float] = 0.0
    follower_count: Optional[int] = 0
    category: Optional[str] = None
    audience_top_country: Optional[str] = None


class FactInfluencerPerformanceCreate(FactInfluencerPerformanceBase):
    """Payload for creating a fact influencer performance record."""


class FactInfluencerPerformance(FactInfluencerPerformanceBase):
    id: int

    class Config:
        orm_mode = True


# -----------------------------
# Fact Content Features
# -----------------------------
class FactContentFeaturesBase(BaseModel):
    content_id: int
    influencer_id: int
    tag_count: Optional[int] = 0
    caption_length: Optional[int] = 0
    content_type: Optional[str] = None
    engagement_rate: Optional[float] = 0.0


class FactContentFeaturesCreate(FactContentFeaturesBase):
    """Payload for creating fact content features."""


class FactContentFeatures(FactContentFeaturesBase):
    id: int

    class Config:
        orm_mode = True


# -----------------------------
# Prediction Logs
# -----------------------------
class PredictionLogBase(BaseModel):
    timestamp: Optional[datetime] = None
    content_id: int
    influencer_id: int
    predicted_engagement: Optional[float] = 0.0
    model_version: str


class PredictionLogCreate(PredictionLogBase):
    """Payload for creating a prediction log."""


class PredictionLog(PredictionLogBase):
    log_id: int

    class Config:
        orm_mode = True


# -----------------------------
# API Logs
# -----------------------------
class APILogBase(BaseModel):
    user: str
    endpoint: str
    status: str
    timestamp: Optional[datetime] = None


class APILogCreate(APILogBase):
    """Payload for creating an API log entry."""


class APILog(APILogBase):
    log_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Brands
# -----------------------------
class BrandBase(BaseModel):
    name: str
    industry: Optional[str] = None
    country: Optional[str] = None
    created_at: Optional[datetime] = None


class BrandCreate(BrandBase):
    """Payload for creating a brand."""


class Brand(BrandBase):
    brand_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Campaigns
# -----------------------------
class CampaignBase(BaseModel):
    brand_id: int
    name: str
    objective: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = 0.0
    status: Optional[str] = None
    created_at: Optional[datetime] = None


class CampaignCreate(CampaignBase):
    """Payload for creating a campaign."""


class Campaign(CampaignBase):
    campaign_id: int

    class Config:
        orm_mode = True


# -----------------------------
# Campaign Content
# -----------------------------
class CampaignContentBase(BaseModel):
    campaign_id: int
    content_id: Optional[int] = None
    influencer_id: Optional[int] = None
    role: Optional[str] = None
    is_paid: Optional[bool] = False
    cost: Optional[float] = 0.0


class CampaignContentCreate(BaseModel):
    """Payload for creating a campaign content association.
    Note: campaign_id comes from the URL path, not the body.
    """
    content_id: Optional[int] = None
    influencer_id: Optional[int] = None
    role: Optional[str] = None
    is_paid: Optional[bool] = False
    cost: Optional[float] = 0.0


class CampaignContent(CampaignContentBase):
    id: int

    class Config:
        orm_mode = True
