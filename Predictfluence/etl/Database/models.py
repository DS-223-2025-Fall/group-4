from sqlalchemy import Column, Integer, String, ForeignKey, Float, Date, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from Database.database import Base

class InfluencerDB(Base):
    __tablename__ = "influencers"

    influencer_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    username = Column(String)
    platform = Column(String)
    follower_count = Column(Integer)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    content = relationship("ContentDB", back_populates="influencer")


class ContentDB(Base):
    __tablename__ = "content"

    content_id = Column(Integer, primary_key=True, index=True)
    influencer_id = Column(Integer, ForeignKey("influencers.influencer_id"))
    content_type = Column(String)
    caption = Column(String)
    post_date = Column(Date)
    url = Column(String)

    influencer = relationship("InfluencerDB", back_populates="content")
    engagement = relationship("EngagementDB", back_populates="content")


class EngagementDB(Base):
    __tablename__ = "engagement"

    engagement_id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("content.content_id"))

    likes = Column(Integer)
    comments = Column(Integer)
    shares = Column(Integer)
    views = Column(Integer)

    engagement_rate = Column(Float)

    content = relationship("ContentDB", back_populates="engagement")