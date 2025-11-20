from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


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
    content_id: int
    role: Optional[str] = None
    is_paid: Optional[bool] = False


class CampaignContentCreate(CampaignContentBase):
    """Payload for creating a campaign content association."""


class CampaignContent(CampaignContentBase):
    id: int

    class Config:
        orm_mode = True

