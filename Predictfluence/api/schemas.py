"""
Pydantic schemas for Predictfluence API responses and requests.
These sit outside the Database package to avoid modifying generated DB models.
"""

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from Database.schema import (
    APILog,
    AudienceDemographics,
    Brand,
    Campaign,
    CampaignContent,
    Content,
    Engagement,
    FactContentFeatures,
    FactInfluencerPerformance,
    Influencer,
)


# -----------------------------
# Auth / Users
# -----------------------------
class LoginRequest(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = None
    company: Optional[str] = None


class UserProfile(BaseModel):
    email: str
    role: Optional[str] = None
    company: Optional[str] = None
    full_name: Optional[str] = None

    class Config:
        orm_mode = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None


# -----------------------------
# Influencers
# -----------------------------
class InfluencerListResponse(BaseModel):
    items: List[Influencer]
    total: int


class InfluencerDetail(BaseModel):
    influencer: Influencer
    performance: Optional[FactInfluencerPerformance] = None
    audience: Optional[List[AudienceDemographics]] = None


class CountResponse(BaseModel):
    count: int


# -----------------------------
# Content / Engagement
# -----------------------------
class ContentDetail(BaseModel):
    content: Content
    engagement: Optional[Engagement] = None
    campaigns: List[int] = Field(default_factory=list)


# -----------------------------
# Brands / Campaigns
# -----------------------------
class CampaignListResponse(BaseModel):
    items: List[Campaign]
    total: int


class CampaignDetail(BaseModel):
    campaign: Campaign
    brand: Optional[Brand] = None
    content_links: List[CampaignContent] = Field(default_factory=list)


class CampaignSummary(BaseModel):
    campaign_id: int
    name: str
    budget: Optional[float] = None
    status: Optional[str] = None
    spend_to_date: float = 0.0
    influencer_count: int = 0
    avg_engagement_rate: float = 0.0
    avg_views: float = 0.0
    avg_cost_per_influencer: float = 0.0


class CampaignInfluencerPerformanceRow(BaseModel):
    influencer_id: int
    content_id: int
    platform: Optional[str] = None
    engagement_rate: Optional[float] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    views: Optional[int] = None
    role: Optional[str] = None
    is_paid: Optional[bool] = None


# -----------------------------
# Analytics
# -----------------------------
class EngagementSeriesPoint(BaseModel):
    date: date
    engagement_rate: float


class EngagementSeriesResponse(BaseModel):
    series: List[EngagementSeriesPoint]


class TopCampaign(BaseModel):
    campaign_id: int
    name: str
    metric_value: float
    rank: int


class TopCampaignsResponse(BaseModel):
    items: List[TopCampaign]


class AudienceAggregate(BaseModel):
    group: Optional[str] = None
    percentage: float


class AudienceAnalyticsResponse(BaseModel):
    group_by: str
    items: List[AudienceAggregate]


class CreativeAnalyticsItem(BaseModel):
    content_type: Optional[str] = None
    topic: Optional[str] = None
    avg_engagement_rate: Optional[float] = None


class CreativeAnalyticsResponse(BaseModel):
    items: List[CreativeAnalyticsItem]


class PerformanceAnalyticsResponse(BaseModel):
    avg_engagement_rate: float
    avg_likes: float
    avg_comments: float
    avg_views: float


# -----------------------------
# Recommendations / ML
# -----------------------------
class RecommendationRequest(BaseModel):
    platform: Optional[str] = None
    audience_size_band: Optional[str] = None
    category: Optional[str] = None
    country: Optional[str] = None
    content_type: Optional[str] = None


class RecommendationItem(BaseModel):
    influencer_id: int
    influencer_name: str
    platform: Optional[str] = None
    predicted_engagement: float
    rationale: str
    content_id: Optional[int] = None


class RecommendationResponse(BaseModel):
    recommendations: List[RecommendationItem]


class MLTrainResponse(BaseModel):
    n_rows: int
    used_synthetic: bool
    r2: Optional[float]
    mae: Optional[float]
    model_version: str
    features: List[str]


class MLPredictRequest(BaseModel):
    follower_count: int
    tag_count: int
    caption_length: int
    content_type: str
    content_id: Optional[int] = None
    influencer_id: Optional[int] = None


class MLPredictResponse(BaseModel):
    predicted_engagement_rate: float
    model_version: str
    logged: bool


# -----------------------------
# Logs / Health
# -----------------------------
class HealthResponse(BaseModel):
    status: str
    db: str


class APILogListResponse(BaseModel):
    items: List[APILog]


# -----------------------------
# Advanced ML / Insights
# -----------------------------
class SkillScoreItem(BaseModel):
    influencer_id: int
    n_posts: int
    mean_residual: float
    shrinkage_weight: float
    skill_score: float


class SkillScoresResponse(BaseModel):
    scores: List[SkillScoreItem]
    model_version: str


class TierPredictRequest(BaseModel):
    follower_count: int
    tag_count: int
    caption_length: int
    content_type: str
    category: Optional[str] = None
    audience_top_country: Optional[str] = None


class TierPredictResponse(BaseModel):
    tier: str
    model_version: str


class TierTrainResponse(BaseModel):
    model_version: str
    accuracy: float
    macro_f1: float
    n_rows: int


class ClusterItem(BaseModel):
    influencer_id: int
    cluster: int
    n_posts: int


class ClusterResponse(BaseModel):
    clusters: List[ClusterItem]
    n_clusters: int


class ScheduleDayItem(BaseModel):
    day_of_week: str
    avg_engagement_rate: float


class ScheduleHourItem(BaseModel):
    post_hour: int
    avg_engagement_rate: float


class ScheduleResponse(BaseModel):
    by_day: Optional[List[ScheduleDayItem]] = None
    by_hour: Optional[List[ScheduleHourItem]] = None
    model_version: str


class BatchScoringResponse(BaseModel):
    output_path: str
    n_predictions: int
    model_version: str
    segments: dict[str, int]
