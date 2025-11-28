import os
import pandas as pd
from sqlalchemy import func
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from Database.database import engine, SessionLocal, Base
from Database.models import (
    InfluencerDB, ContentDB, EngagementDB, AudienceDemographicsDB,
    FactInfluencerPerformanceDB, FactContentFeaturesDB,
    CampaignDB, CampaignContentDB, UserDB
)

CSV_FOLDER = os.getenv("CSV_FOLDER", "data")
os.makedirs(CSV_FOLDER, exist_ok=True)

# ----------------------------
# Generic CSV loader
# ----------------------------
def load_csv(session: Session, csv_file: str, orm_class, hash_password=False):
    path = os.path.join(CSV_FOLDER, csv_file)
    if not os.path.exists(path):
        print(f"CSV not found: {path}, skipping")
        return
    df = pd.read_csv(path)
    for col in df.columns:
        if any(x in col.lower() for x in ["date", "timestamp", "created"]):
            df[col] = pd.to_datetime(df[col], errors="coerce")
    records = []
    for _, row in df.iterrows():
        data = row.to_dict()
        if hash_password and "plain_password" in data:
            data["hashed_password"] = bcrypt.hash(data.pop("plain_password"))
        records.append(orm_class(**data))
    if records:
        session.add_all(records)
        session.commit()

# ----------------------------
# ETL process
# ----------------------------
def run_etl():
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        # ----------------------------
        # Load CSVs
        # ----------------------------
        load_csv(session, "users.csv", UserDB, hash_password=True)
        load_csv(session, "influencers.csv", InfluencerDB)
        load_csv(session, "content.csv", ContentDB)
        load_csv(session, "engagement.csv", EngagementDB)
        load_csv(session, "audience_demographics.csv", AudienceDemographicsDB)

        # ----------------------------
        # Fact Influencer Performance
        # ----------------------------
        influencer_records = []
        influencers = session.query(InfluencerDB).all()
        for influencer in influencers:
            engagements = (
                session.query(EngagementDB)
                .join(ContentDB, EngagementDB.content_id == ContentDB.content_id)
                .filter(ContentDB.influencer_id == influencer.influencer_id)
                .all()
            )
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
            influencer_records.append(FactInfluencerPerformanceDB(
                influencer_id=influencer.influencer_id,
                avg_engagement_rate=avg_eng_rate,
                avg_likes=avg_likes,
                avg_comments=avg_comments,
                avg_shares=avg_shares,
                avg_views=avg_views,
                follower_count=influencer.follower_count,
                category=influencer.category,
                audience_top_country=top_country.country if top_country else None
            ))
        session.add_all(influencer_records)
        session.commit()

        # ----------------------------
        # Fact Content Features
        # ----------------------------
        contents = session.query(ContentDB).all()
        content_records = []
        engagement_map = {e.content_id: e.engagement_rate for e in session.query(EngagementDB).all()}
        for content in contents:
            content_records.append(FactContentFeaturesDB(
                content_id=content.content_id,
                influencer_id=content.influencer_id,
                tag_count=0,
                caption_length=len(content.caption) if content.caption else 0,
                content_type=content.content_type,
                engagement_rate=engagement_map.get(content.content_id, 0.0)
            ))
        session.add_all(content_records)
        session.commit()

        # ----------------------------
        # Populate Campaign Content with cost
        # ----------------------------
        campaigns = session.query(CampaignDB).all()
        campaign_content_records = []
        for campaign in campaigns:
            for content in contents:
                if (campaign.campaign_id + content.influencer_id) % 3 == 0:
                    role = "primary" if (content.content_id + campaign.campaign_id) % 2 == 0 else "supporting"
                    is_paid = (content.content_id + campaign.campaign_id) % 2 == 0
                    cost = 50.0 + ((content.content_id + campaign.campaign_id) % 100)
                    campaign_content_records.append(CampaignContentDB(
                        campaign_id=campaign.campaign_id,
                        content_id=content.content_id,
                        role=role,
                        is_paid=is_paid,
                        cost=cost
                    ))
        session.add_all(campaign_content_records)
        session.commit()

        # ----------------------------
        # Compute spend_to_date for campaigns
        # ----------------------------
        for campaign in campaigns:
            spend = session.query(func.sum(CampaignContentDB.cost)).filter(
                CampaignContentDB.campaign_id == campaign.campaign_id
            ).scalar() or 0.0
            campaign.spend_to_date = spend
        session.commit()

        print("ETL with Users and Campaign Finance completed successfully.")
    finally:
        session.close()


if __name__ == "__main__":
    run_etl()
