"""
SQLAlchemy ORM models that mirror the Predictfluence ERD.
"""

from datetime import datetime
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
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class InfluencerDB(Base):
    __tablename__ = "influencers"

    influencer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    follower_count = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

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


class ContentDB(Base):
    __tablename__ = "content"

    content_id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(
        Integer, ForeignKey("influencers.influencer_id"), nullable=False
    )
    content_type = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    post_date = Column(Date, nullable=True)
    caption = Column(Text, nullable=True)
    url = Column(String, nullable=True)

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

    influencer = relationship("InfluencerDB", back_populates="audiences")


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


class PredictionLogDB(Base):
    __tablename__ = "prediction_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    content_id = Column(Integer, ForeignKey("content.content_id"), nullable=False)
    influencer_id = Column(
        Integer, ForeignKey("influencers.influencer_id"), nullable=False
    )
    predicted_engagement = Column(Float, default=0.0)
    model_version = Column(String, nullable=False)

    content = relationship("ContentDB", back_populates="prediction_logs")
    influencer = relationship("InfluencerDB", back_populates="prediction_logs")


class APILogDB(Base):
    __tablename__ = "api_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    user = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class BrandDB(Base):
    __tablename__ = "brands"

    brand_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    country = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaigns = relationship(
        "CampaignDB", back_populates="brand", cascade="all, delete-orphan"
    )


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
    created_at = Column(DateTime, default=datetime.utcnow)

    brand = relationship("BrandDB", back_populates="campaigns")
    campaign_content = relationship(
        "CampaignContentDB", back_populates="campaign", cascade="all, delete-orphan"
    )


class CampaignContentDB(Base):
    __tablename__ = "campaign_content"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.campaign_id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content.content_id"), nullable=False)
    role = Column(String, nullable=True)
    is_paid = Column(Boolean, default=False)

    campaign = relationship("CampaignDB", back_populates="campaign_content")
    content = relationship("ContentDB", back_populates="campaign_links")
