import os
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError

from Database.database import engine, SessionLocal, Base
from Database.models import (
    InfluencerDB, ContentDB, EngagementDB, AudienceDemographicsDB,
    FactInfluencerPerformanceDB, FactContentFeaturesDB,
    CampaignDB, CampaignContentDB
)

# ----------------------------
# CSV folder
# ----------------------------
CSV_FOLDER = os.getenv("CSV_FOLDER", "csv_data")
os.makedirs(CSV_FOLDER, exist_ok=True)

# ----------------------------
# Pydantic models for CSV validation
# ----------------------------
class InfluencerModel(BaseModel):
    influencer_id: int | None
    name: str
    username: str
    platform: str
    follower_count: int
    category: str
    created_at: datetime | None = None

class ContentModel(BaseModel):
    content_id: int | None
    influencer_id: int
    content_type: str
    topic: str | None = None
    post_date: datetime | None = None
    caption: str | None = None
    url: str | None = None

class EngagementModel(BaseModel):
    engagement_id: int | None
    content_id: int
    likes: int = 0
    comments: int = 0
    shares: int = 0
    views: int = 0
    engagement_rate: float = 0.0

class AudienceDemographicsModel(BaseModel):
    audience_id: int | None
    influencer_id: int
    age_group: str | None = None
    gender: str | None = None
    country: str | None = None
    percentage: float = 0.0

# ----------------------------
# Load CSV into DB
# ----------------------------
def load_csv(session: Session, csv_file: str, model_class, orm_class):
    path = os.path.join(CSV_FOLDER, csv_file)
    if not os.path.exists(path):
        print(f"CSV not found: {path}, skipping")
        return

    df = pd.read_csv(path)

    # Convert date columns
    for col in df.columns:
        if "date" in col or "timestamp" in col or "created_at" in col:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    for _, row in df.iterrows():
        try:
            validated = model_class(**row.to_dict())
        except ValidationError as e:
            print(f"Skipping row due to validation error: {e}")
            continue
        obj = orm_class(**validated.dict(exclude_none=True))
        session.add(obj)
    session.commit()


# ----------------------------
# ETL Process
# ----------------------------
def run_etl():
    # Create tables
    Base.metadata.create_all(engine)

    session = SessionLocal()

    try:
        # Load base CSVs
        load_csv(session, "influencers.csv", InfluencerModel, InfluencerDB)
        load_csv(session, "content.csv", ContentModel, ContentDB)
        load_csv(session, "engagement.csv", EngagementModel, EngagementDB)
        load_csv(session, "audience_demographics.csv", AudienceDemographicsModel, AudienceDemographicsDB)

        # ----------------------------
        # Populate fact influencer performance
        # ----------------------------
        influencers = session.query(InfluencerDB).all()
        for influencer in influencers:
            engagements = session.query(EngagementDB).join(ContentDB).filter(ContentDB.influencer_id == influencer.influencer_id).all()
            if engagements:
                avg_eng_rate = sum(e.engagement_rate for e in engagements) / len(engagements)
                avg_likes = sum(e.likes for e in engagements) / len(engagements)
                avg_comments = sum(e.comments for e in engagements) / len(engagements)
                avg_shares = sum(e.shares for e in engagements) / len(engagements)
                avg_views = sum(e.views for e in engagements) / len(engagements)
            else:
                avg_eng_rate = avg_likes = avg_comments = avg_shares = avg_views = 0.0

            top_country = (
                session.query(AudienceDemographicsDB)
                .filter(AudienceDemographicsDB.influencer_id == influencer.influencer_id)
                .order_by(AudienceDemographicsDB.percentage.desc())
                .first()
            )
            obj = FactInfluencerPerformanceDB(
                influencer_id=influencer.influencer_id,
                avg_engagement_rate=avg_eng_rate,
                avg_likes=avg_likes,
                avg_comments=avg_comments,
                avg_shares=avg_shares,
                avg_views=avg_views,
                follower_count=influencer.follower_count,
                category=influencer.category,
                audience_top_country=top_country.country if top_country else None
            )
            session.add(obj)
        session.commit()

        # ----------------------------
        # Populate fact content features
        # ----------------------------
        contents = session.query(ContentDB).all()
        for content in contents:
            engagement = session.query(EngagementDB).filter(EngagementDB.content_id == content.content_id).first()
            obj = FactContentFeaturesDB(
                content_id=content.content_id,
                influencer_id=content.influencer_id,
                tag_count=0,
                caption_length=len(content.caption) if content.caption else 0,
                content_type=content.content_type,
                engagement_rate=engagement.engagement_rate if engagement else 0.0
            )
            session.add(obj)
        session.commit()

        # ----------------------------
        # Populate campaign content deterministically
        # ----------------------------
        campaigns = session.query(CampaignDB).all()
        for campaign in campaigns:
            for content in contents:
                if (campaign.campaign_id + content.influencer_id) % 3 == 0:
                    role = ["primary", "supporting"][(content.content_id + campaign.campaign_id) % 2]
                    is_paid = ((content.content_id + campaign.campaign_id) % 2 == 0)
                    obj = CampaignContentDB(
                        campaign_id=campaign.campaign_id,
                        content_id=content.content_id,
                        role=role,
                        is_paid=is_paid
                    )
                    session.add(obj)
        session.commit()

        print("ETL completed successfully")

    finally:
        session.close()


if __name__ == "__main__":
    run_etl()
