"""
SQLAlchemy ORM Models for Predictfluence Influencer Marketing Project.

This module defines the database schema using SQLAlchemy's declarative ORM.
The models mirror the ERD for the project and are used throughout the ETL
pipeline, API, and analytics components.

Key Concepts:
- Each class represents a table in the database.
- Relationships are defined using SQLAlchemy's `relationship`.
- Indexes are added for performance on frequently queried columns.
- Fact tables store aggregated metrics for influencers and content.
- Prediction logs and API logs track model predictions and API usage.

Tables / Models:
- UserDB: Application users with hashed passwords and roles.
- InfluencerDB: Influencer metadata and relationships to content and audience.
- ContentDB: Individual posts by influencers.
- EngagementDB: Engagement metrics for content (likes, comments, shares, views, rate).
- AudienceDemographicsDB: Demographic breakdown of an influencer's audience.
- FactInfluencerPerformanceDB: Aggregated influencer-level performance metrics.
- FactContentFeaturesDB: Aggregated content-level features.
- PredictionLogDB: Model prediction logs for influencer content.
- APILogDB: Tracks API requests and responses.
- BrandDB: Brands participating in campaigns.
- CampaignDB: Campaigns run by brands, linked to content.
- CampaignContentDB: Links content to campaigns with cost and role information.

Usage:
1. Import the `Base` class for SQLAlchemy table creation.
2. Import individual models for querying or ETL operations.
3. Use relationships for joining tables efficiently in queries.

Notes:
- Timestamps are stored in UTC by default.
- Cascade deletes ensure dependent rows are removed automatically.
- Indexes improve query performance on commonly filtered or joined columns.

Example:
    from Database.models import Base, UserDB, InfluencerDB
    from Database.database import engine

    # Create all tables
    Base.metadata.create_all(bind=engine)
"""
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Index,
    func
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


# ============================================================
# Users
# ============================================================
class UserDB(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=True)
    company = Column(String, nullable=True)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('utc', func.now()))


# ============================================================
# Influencers
# ============================================================
class InfluencerDB(Base):
    __tablename__ = "influencers"

    influencer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    follower_count = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('utc', func.now()))

    __table_args__ = (
        Index("idx_influencer_platform_category_followers",
              "platform", "category", "follower_count"),
    )

    content = relationship(
        "ContentDB", back_populates="influencer", cascade="all, delete-orphan"
    )
    audiences = relationship(
        "AudienceDemographicsDB",
        back_populates="influencer",
        cascade="all, delete-orphan",
    )
    fact_performance = relationship(
        "FactInfluencerPerformanceDB",
        back_populates="influencer",
        cascade="all, delete-orphan",
        uselist=False,
    )
    fact_content_features = relationship(
        "FactContentFeaturesDB", back_populates="influencer", cascade="all, delete-orphan"
    )
    prediction_logs = relationship(
        "PredictionLogDB", back_populates="influencer", cascade="all, delete-orphan"
    )


# ============================================================
# Content
# ============================================================
class ContentDB(Base):
    __tablename__ = "content"

    content_id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(
        Integer, ForeignKey("influencers.influencer_id"), nullable=False
    )
    content_type = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    post_date = Column(Date, nullable=True)
    post_datetime = Column(DateTime(timezone=True), nullable=True)  # For hour-level posting schedule analysis
    caption = Column(Text, nullable=True)
    url = Column(String, nullable=True)

    __table_args__ = (
        Index("idx_content_post_date_content_type", "post_date", "content_type"),
        Index("idx_content_post_datetime", "post_datetime"),
    )

    influencer = relationship("InfluencerDB", back_populates="content")
    engagement = relationship(
        "EngagementDB", back_populates="content", cascade="all, delete-orphan"
    )
    fact_features = relationship(
        "FactContentFeaturesDB", back_populates="content", cascade="all, delete-orphan"
    )
    prediction_logs = relationship(
        "PredictionLogDB", back_populates="content", cascade="all, delete-orphan"
    )
    campaign_links = relationship(
        "CampaignContentDB", back_populates="content", cascade="all, delete-orphan"
    )


# ============================================================
# Engagement
# ============================================================
class EngagementDB(Base):
    __tablename__ = "engagement"

    engagement_id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.content_id"), nullable=False)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    content = relationship("ContentDB", back_populates="engagement")


# ============================================================
# Audience Demographics
# ============================================================
class AudienceDemographicsDB(Base):
    __tablename__ = "audience_demographics"

    audience_id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(
        Integer, ForeignKey("influencers.influencer_id"), nullable=False
    )
    age_group = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    country = Column(String, nullable=True)
    percentage = Column(Float, default=0.0)

    __table_args__ = (
        Index("idx_audience_age_gender_country", "age_group", "gender", "country"),
    )

    influencer = relationship("InfluencerDB", back_populates="audiences")


# ============================================================
# Fact Influencer Performance
# ============================================================
class FactInfluencerPerformanceDB(Base):
    __tablename__ = "fact_influencer_performance"

    id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(
        Integer, ForeignKey("influencers.influencer_id"), nullable=False, unique=True
    )
    avg_engagement_rate = Column(Float, default=0.0)
    avg_likes = Column(Float, default=0.0)
    avg_comments = Column(Float, default=0.0)
    avg_shares = Column(Float, default=0.0)
    avg_views = Column(Float, default=0.0)
    follower_count = Column(Integer, default=0)
    category = Column(String, nullable=True)
    audience_top_country = Column(String, nullable=True)

    influencer = relationship("InfluencerDB", back_populates="fact_performance")


# ============================================================
# Fact Content Features
# ============================================================
class FactContentFeaturesDB(Base):
    __tablename__ = "fact_content_features"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.content_id"), nullable=False)
    influencer_id = Column(
        Integer, ForeignKey("influencers.influencer_id"), nullable=False
    )
    tag_count = Column(Integer, default=0)
    caption_length = Column(Integer, default=0)
    content_type = Column(String, nullable=True)
    engagement_rate = Column(Float, default=0.0)

    content = relationship("ContentDB", back_populates="fact_features")
    influencer = relationship("InfluencerDB", back_populates="fact_content_features")


# ============================================================
# Prediction Logs
# ============================================================
class PredictionLogDB(Base):
    __tablename__ = "prediction_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.timezone('utc', func.now()))
    content_id = Column(Integer, ForeignKey("content.content_id"), nullable=False)
    influencer_id = Column(
        Integer, ForeignKey("influencers.influencer_id"), nullable=False
    )
    predicted_engagement = Column(Float, default=0.0)
    model_version = Column(String, nullable=False)

    content = relationship("ContentDB", back_populates="prediction_logs")
    influencer = relationship("InfluencerDB", back_populates="prediction_logs")


# ============================================================
# API Logs
# ============================================================
class APILogDB(Base):
    __tablename__ = "api_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    user = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.timezone('utc', func.now()))


# ============================================================
# Brands
# ============================================================
class BrandDB(Base):
    __tablename__ = "brands"

    brand_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    country = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('utc', func.now()))

    campaigns = relationship(
        "CampaignDB", back_populates="brand", cascade="all, delete-orphan"
    )


# ============================================================
# Campaigns
# ============================================================
class CampaignDB(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(Integer, ForeignKey("brands.brand_id"), nullable=False)
    name = Column(String, nullable=False)
    objective = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    budget = Column(Float, default=0.0)
    status = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.timezone('utc', func.now()))

    __table_args__ = (
        Index("idx_campaign_status_dates", "status", "start_date", "end_date"),
    )

    brand = relationship("BrandDB", back_populates="campaigns")
    campaign_content = relationship(
        "CampaignContentDB", back_populates="campaign", cascade="all, delete-orphan"
    )


# ============================================================
# Campaign Content
# ============================================================
class CampaignContentDB(Base):
    __tablename__ = "campaign_content"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.content_id"), nullable=False)
    role = Column(String, nullable=True)
    is_paid = Column(Boolean, default=False)
    cost = Column(Float, default=0.0)

    campaign = relationship("CampaignDB", back_populates="campaign_content")
    content = relationship("ContentDB", back_populates="campaign_links")
