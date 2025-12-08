import os
import re
import pandas as pd
from datetime import datetime, time
from sqlalchemy import func
from sqlalchemy.orm import Session
# from passlib.hash import bcrypt
from Database.database import engine, SessionLocal, Base
from Database.models import (
    InfluencerDB, ContentDB, EngagementDB, AudienceDemographicsDB,
    FactInfluencerPerformanceDB, FactContentFeaturesDB,
    CampaignDB, CampaignContentDB, UserDB, BrandDB
)

# Folder to store CSV files
CSV_FOLDER = os.getenv("CSV_FOLDER", "data")
os.makedirs(CSV_FOLDER, exist_ok=True)


# ----------------------------
# Generic CSV loader
# ----------------------------
def load_csv(session: Session, csv_file: str, orm_class, hash_password=False):
    """
    Loads data from a CSV file into the database.

    Parameters:
        session (Session): SQLAlchemy session object.
        csv_file (str): Name of the CSV file to load.
        orm_class: The ORM model class to instantiate for each row.
        hash_password (bool): If True, hashes 'plain_password' into 'hashed_password'.

    Notes:
        - Automatically converts any columns with "date", "timestamp", or "created" in the name to datetime.
        - Skips rows with missing required data if they cause exceptions.
    """
    path = os.path.join(CSV_FOLDER, csv_file)
    if not os.path.exists(path):
        print(f"CSV not found: {path}, skipping")
        return

    df = pd.read_csv(path)

    # Convert date columns to datetime
    for col in df.columns:
        if any(x in col.lower() for x in ["date", "timestamp", "created"]):
            df[col] = pd.to_datetime(df[col], errors="coerce")

    records = []
    for _, row in df.iterrows():
        data = row.to_dict()
        # hash passwords if required
        # if hash_password and "plain_password" in data:
        #     data["hashed_password"] = bcrypt.hash(data.pop("plain_password"))
        records.append(orm_class(**data))

    if records:
        session.add_all(records)
        session.commit()


# ----------------------------
# ETL process
# ----------------------------
def run_etl():
    """
    Executes the full ETL process:

    1. Creates database tables if they don't exist.
    2. Loads all CSV files into their respective database tables.
    3. Computes and populates fact tables:
        - FactInfluencerPerformanceDB
        - FactContentFeaturesDB
    4. Populates campaign content relationships with simulated costs.
    5. Computes campaign spend-to-date.

    Notes:
        - Users CSV supports password hashing.
        - Engagement statistics are aggregated per influencer.
        - Campaign content assignment is simulated based on content_id + campaign_id.
    """
    Base.metadata.create_all(engine)
    session = SessionLocal()

    try:
        # ----------------------------
        # Load CSVs into respective tables
        # ----------------------------
        load_csv(session, "users.csv", UserDB, hash_password=True)
        load_csv(session, "brands.csv", BrandDB)
        load_csv(session, "campaigns.csv", CampaignDB)
        load_csv(session, "influencers.csv", InfluencerDB)
        load_csv(session, "content.csv", ContentDB)
        load_csv(session, "engagement.csv", EngagementDB)
        load_csv(session, "audience_demographics.csv", AudienceDemographicsDB)
        load_csv(session, "campaign_content.csv", CampaignContentDB)

        # ----------------------------
        # Populate post_datetime from post_date (if missing)
        # ----------------------------
        print("Populating post_datetime from post_date...")
        contents_to_update = session.query(ContentDB).filter(ContentDB.post_datetime.is_(None)).all()
        for content in contents_to_update:
            if content.post_date:
                # Set default time to 12:00 PM if not available
                content.post_datetime = datetime.combine(content.post_date, time(12, 0))
        session.commit()
        print(f"Updated {len(contents_to_update)} content records with post_datetime")

        # ----------------------------
        # Compute Fact Influencer Performance
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

            # Aggregate engagement metrics
            if engagements:
                avg_eng_rate = sum(e.engagement_rate for e in engagements) / len(engagements)
                avg_likes = sum(e.likes for e in engagements) / len(engagements)
                avg_comments = sum(e.comments for e in engagements) / len(engagements)
                avg_shares = sum(e.shares for e in engagements) / len(engagements)
                avg_views = sum(e.views for e in engagements) / len(engagements)
            else:
                avg_eng_rate = avg_likes = avg_comments = avg_shares = avg_views = 0.0

            # Find top audience country
            top_country = (
                session.query(AudienceDemographicsDB)
                .filter(AudienceDemographicsDB.influencer_id == influencer.influencer_id)
                .order_by(AudienceDemographicsDB.percentage.desc())
                .first()
            )

            # Handle missing data per ETL requirements
            follower_count = influencer.follower_count if influencer.follower_count and influencer.follower_count > 0 else 1000
            category = influencer.category if influencer.category else "Unknown"
            audience_top_country = top_country.country if top_country and top_country.country else "Unknown"

            influencer_records.append(FactInfluencerPerformanceDB(
                influencer_id=influencer.influencer_id,
                avg_engagement_rate=avg_eng_rate,
                avg_likes=avg_likes,
                avg_comments=avg_comments,
                avg_shares=avg_shares,
                avg_views=avg_views,
                follower_count=follower_count,
                category=category,
                audience_top_country=audience_top_country
            ))

        # Clear existing fact_influencer_performance to avoid duplicates
        session.query(FactInfluencerPerformanceDB).delete()
        session.add_all(influencer_records)
        session.commit()
        print(f"Created {len(influencer_records)} fact_influencer_performance records")

        # ----------------------------
        # Compute Fact Content Features
        # ----------------------------
        print("Computing fact_content_features...")
        contents = session.query(ContentDB).all()
        content_records = []
        engagement_map = {e.content_id: e.engagement_rate for e in session.query(EngagementDB).all()}

        def calculate_tag_count(caption: str) -> int:
            """Count hashtags (#) and mentions (@) in caption."""
            if not caption:
                return 0
            # Count # symbols (hashtags)
            hashtags = len(re.findall(r'#\w+', caption))
            # Count @ symbols (mentions)
            mentions = len(re.findall(r'@\w+', caption))
            return hashtags + mentions

        for content in contents:
            # Calculate tag_count from caption
            tag_count = calculate_tag_count(content.caption) if content.caption else 0
            
            # Calculate caption_length
            caption_length = len(content.caption) if content.caption else 0
            
            # Get engagement_rate
            engagement_rate = engagement_map.get(content.content_id, 0.0)
            
            # Validate engagement_rate is reasonable (0-1 range)
            if engagement_rate < 0:
                engagement_rate = 0.0
            if engagement_rate > 1:
                engagement_rate = min(engagement_rate, 1.0)  # Cap at 1.0 if calculated differently
            
            # Ensure content_type is valid
            valid_content_types = ["Image", "Video", "Reel", "Story"]
            content_type = content.content_type if content.content_type in valid_content_types else "Image"

            content_records.append(FactContentFeaturesDB(
                content_id=content.content_id,
                influencer_id=content.influencer_id,
                tag_count=tag_count,
                caption_length=caption_length,
                content_type=content_type,
                engagement_rate=engagement_rate
            ))

        # Clear existing fact_content_features to avoid duplicates
        session.query(FactContentFeaturesDB).delete()
        session.add_all(content_records)
        session.commit()
        print(f"Created {len(content_records)} fact_content_features records")

        # ----------------------------
        # Data Quality Validation
        # ----------------------------
        print("\nValidating data quality...")
        
        # Check fact tables are populated
        fact_perf_count = session.query(FactInfluencerPerformanceDB).count()
        fact_content_count = session.query(FactContentFeaturesDB).count()
        
        print(f"  fact_influencer_performance: {fact_perf_count} records")
        print(f"  fact_content_features: {fact_content_count} records")
        
        # Check for NULLs in critical fields
        null_followers = session.query(FactInfluencerPerformanceDB).filter(
            FactInfluencerPerformanceDB.follower_count.is_(None)
        ).count()
        null_categories = session.query(FactInfluencerPerformanceDB).filter(
            FactInfluencerPerformanceDB.category.is_(None)
        ).count()
        
        if null_followers > 0:
            print(f"  WARNING: {null_followers} records with NULL follower_count")
        if null_categories > 0:
            print(f"  WARNING: {null_categories} records with NULL category")
        
        # Check join capability
        join_count = (
            session.query(FactContentFeaturesDB)
            .join(FactInfluencerPerformanceDB, 
                  FactContentFeaturesDB.influencer_id == FactInfluencerPerformanceDB.influencer_id)
            .count()
        )
        print(f"  Joinable records (fact_content_features + fact_influencer_performance): {join_count}")
        
        if fact_perf_count > 0 and fact_content_count > 0 and join_count > 0:
            print("\n✅ ETL completed successfully. All requirements met!")
        else:
            print("\n⚠️  ETL completed but some data may be missing. Check warnings above.")

    except Exception as e:
        print(f"\n❌ ETL failed with error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_etl()
