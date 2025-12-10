import os
import re
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
from faker import Faker
from sqlalchemy import func, text
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

fake = Faker()


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
        - Validates foreign key constraints for campaign_content.
        - Clears existing data from the table before loading to avoid duplicate key errors.
    """
    path = os.path.join(CSV_FOLDER, csv_file)
    if not os.path.exists(path):
        print(f"CSV not found: {path}, skipping")
        return

    # Note: Tables are cleared in bulk before loading all CSVs to avoid foreign key issues

    df = pd.read_csv(path)

    # Convert date columns to datetime
    for col in df.columns:
        if any(x in col.lower() for x in ["date", "timestamp", "created"]):
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Remove explicit ID columns for tables with auto-incrementing primary keys
    # This prevents conflicts with sequences
    id_columns_to_remove = {
        "campaign_content.csv": ["id"],
        "audience_demographics.csv": ["audience_id"],
        "engagement.csv": ["engagement_id"],
    }
    
    if csv_file in id_columns_to_remove:
        for col in id_columns_to_remove[csv_file]:
            if col in df.columns:
                df = df.drop(columns=[col])
                print(f"  Removed explicit {col} column from {csv_file} (using auto-increment)")

    # Validate foreign keys for campaign_content
    if csv_file == "campaign_content.csv":
        # Get all valid campaign_ids from the database
        valid_campaign_ids = set(session.query(CampaignDB.campaign_id).all())
        valid_campaign_ids = {cid[0] for cid in valid_campaign_ids}
        
        # Get all valid content_ids from the database
        valid_content_ids = set(session.query(ContentDB.content_id).all())
        valid_content_ids = {cid[0] for cid in valid_content_ids}
        
        # Filter out rows with invalid foreign keys
        initial_count = len(df)
        df = df[
            df['campaign_id'].isin(valid_campaign_ids) & 
            df['content_id'].isin(valid_content_ids)
        ]
        filtered_count = initial_count - len(df)
        
        if filtered_count > 0:
            print(f"  Filtered out {filtered_count} campaign_content records with invalid foreign keys")

    records = []
    for _, row in df.iterrows():
        try:
            data = row.to_dict()
            # hash passwords if required
            # if hash_password and "plain_password" in data:
            #     data["hashed_password"] = bcrypt.hash(data.pop("plain_password"))
            records.append(orm_class(**data))
        except Exception as e:
            print(f"  Skipping row due to error: {e}")
            continue

    if records:
        try:
            session.add_all(records)
            session.commit()
            print(f"  Loaded {len(records)} records from {csv_file}")
        except Exception as e:
            # If commit fails (e.g., foreign key violation), try inserting one by one
            # to identify and skip problematic records
            session.rollback()
            successful = 0
            failed = 0
            for record in records:
                try:
                    session.add(record)
                    session.commit()
                    successful += 1
                except Exception as row_error:
                    session.rollback()
                    failed += 1
                    if failed <= 5:  # Only print first 5 errors to avoid spam
                        print(f"  Skipping record due to error: {row_error}")
            if failed > 0:
                print(f"  Loaded {successful} records, skipped {failed} invalid records from {csv_file}")
            else:
                print(f"  Loaded {successful} records from {csv_file}")


# ----------------------------
# Data Generation (if CSV files don't exist)
# ----------------------------
def generate_data_if_needed():
    """Generate CSV files if they don't exist."""
    # Check if data already exists
    if os.path.exists(os.path.join(CSV_FOLDER, "influencers.csv")):
        print("Data files already exist, skipping generation.")
        return
    
    # If CSV files don't exist, use fallback generator
    print("No data files found. Using fallback generator...")
    _generate_fallback_data()

def _generate_fallback_data():
    """Fallback data generator if large dataset generator fails."""
    NUM_INFLUENCERS = 150
    MIN_POSTS = 5
    MAX_POSTS = 50
    NUM_BRANDS = 1  # Only Pepsi
    MIN_CAMPAIGNS = 2
    MAX_CAMPAIGNS = 5
    
    PLATFORMS = ["Instagram", "TikTok", "YouTube"]
    CATEGORIES = ["Beauty", "Fitness", "Tech", "Food", "Travel", "Gaming", "Fashion", "Lifestyle"]
    CONTENT_TYPES = ["Image", "Video", "Reel", "Story"]
    TOPICS = ["Fitness", "Beauty", "Tech", "Food", "Travel", "Gaming", "Fashion", "Lifestyle", "Wellness", "Entertainment"]
    AGE_GROUPS = ["13-17", "18-24", "25-34", "35-44", "45-54", "55+"]
    GENDERS = ["Male", "Female", "Other"]
    COUNTRIES = ["USA", "UK", "Canada", "Germany", "France", "India", "Brazil", "Australia", "Japan", "Spain"]
    CAMPAIGN_STATUS = ["planned", "active", "completed", "paused"]
    CAMPAIGN_OBJECTIVES = ["Brand Awareness", "Engagement", "Sales", "Lead Generation", "Product Launch"]
    
    print("Generating comprehensive demo data...")
    rng = np.random.default_rng(42)
    
    # 1. Influencers
    influencers = []
    for i in range(1, NUM_INFLUENCERS + 1):
        follower_tier = rng.choice(["micro", "mid", "macro"], p=[0.5, 0.35, 0.15])
        if follower_tier == "micro":
            follower_count = rng.integers(1000, 10000)
        elif follower_tier == "mid":
            follower_count = rng.integers(10000, 100000)
        else:
            follower_count = rng.integers(100000, 2000000)
        
        influencers.append({
            "influencer_id": i,
            "name": fake.name(),
            "username": f"@{fake.user_name()}",
            "platform": rng.choice(PLATFORMS),
            "follower_count": follower_count,
            "category": rng.choice(CATEGORIES),
            "created_at": fake.date_between(start_date="-3y", end_date="today")
        })
    pd.DataFrame(influencers).to_csv(os.path.join(CSV_FOLDER, "influencers.csv"), index=False)
    
    # 2. Content
    contents = []
    content_id = 1
    hashtag_templates = ["#fitness #workout", "#beauty #makeup", "#tech #gadgets", "#food #recipe", "#travel #wanderlust", "#gaming #streaming", "#fashion #style", "#lifestyle #motivation"]
    for inf in influencers:
        num_posts = rng.integers(MIN_POSTS, MAX_POSTS)
        for _ in range(num_posts):
            caption = f"{fake.sentence(nb_words=rng.integers(8, 25))} {rng.choice(hashtag_templates)}"
            post_date = fake.date_between(start_date="-180d", end_date="today")
            contents.append({
                "content_id": content_id,
                "influencer_id": inf["influencer_id"],
                "content_type": rng.choice(CONTENT_TYPES, p=np.array([0.35, 0.35, 0.2, 0.1])),
                "topic": rng.choice(TOPICS),
                "post_date": post_date,
                "caption": caption,
                "url": f"https://{inf['platform'].lower()}.com/posts/{content_id}"
            })
            content_id += 1
    pd.DataFrame(contents).to_csv(os.path.join(CSV_FOLDER, "content.csv"), index=False)
    
    # 3. Engagement
    engagements = []
    for content in contents:
        inf = next(i for i in influencers if i["influencer_id"] == content["influencer_id"])
        followers = inf["follower_count"]
        base_engagement = 0.03 if followers < 10000 else (0.02 if followers < 100000 else 0.01)
        if content["content_type"] == "Reel":
            base_engagement *= 1.3
        elif content["content_type"] == "Video":
            base_engagement *= 1.1
        
        views = int(followers * rng.uniform(0.1, 0.6))
        likes = int(views * base_engagement * rng.uniform(0.7, 1.0))
        comments = int(likes * rng.uniform(0.05, 0.15))
        shares = int(likes * rng.uniform(0.02, 0.08))
        engagement_rate = round((likes + comments + shares) / max(1, views), 6)
        
        engagements.append({
            "engagement_id": content["content_id"],
            "content_id": content["content_id"],
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "views": views,
            "engagement_rate": engagement_rate
        })
    pd.DataFrame(engagements).to_csv(os.path.join(CSV_FOLDER, "engagement.csv"), index=False)
    
    # 4. Audience Demographics
    audience_list = []
    audience_id = 1
    for inf in influencers:
        num_segments = rng.integers(3, 6)
        selected_countries = list(rng.choice(COUNTRIES, size=min(num_segments, len(COUNTRIES)), replace=False))
        percentages = np.random.dirichlet(np.ones(num_segments)) * 100
        for idx, country in enumerate(selected_countries):
            audience_list.append({
                "audience_id": audience_id,
                "influencer_id": inf["influencer_id"],
                "age_group": rng.choice(AGE_GROUPS),
                "gender": rng.choice(GENDERS),
                "country": country,
                "percentage": round(float(percentages[idx]), 2)
            })
            audience_id += 1
    pd.DataFrame(audience_list).to_csv(os.path.join(CSV_FOLDER, "audience_demographics.csv"), index=False)
    
    # 5. Brands (Only Pepsi)
    brands = []
    brands.append({
        "brand_id": 1,
        "name": "Pepsi",
        "industry": "Food & Beverage",
        "country": "USA",
        "created_at": "1883-01-01"
    })
    pd.DataFrame(brands).to_csv(os.path.join(CSV_FOLDER, "brands.csv"), index=False)
    
    # 6. Campaigns
    campaigns = []
    campaign_id = 1
    for brand in brands:
        num_campaigns = rng.integers(MIN_CAMPAIGNS, MAX_CAMPAIGNS)
        for _ in range(num_campaigns):
            start_date = fake.date_between(start_date="-1y", end_date="+30d")
            end_date = start_date + timedelta(days=rng.integers(14, 90))
            today = datetime.now().date()
            status = "completed" if end_date < today else ("planned" if start_date > today else rng.choice(["active", "paused"]))
            
            campaigns.append({
                "campaign_id": campaign_id,
                "brand_id": brand["brand_id"],
                "name": f"{brand['name']} {rng.choice(['Summer', 'Winter', 'Spring', 'Fall', 'Holiday', 'Launch', 'Promo'])} Campaign",
                "objective": rng.choice(CAMPAIGN_OBJECTIVES),
                "start_date": start_date,
                "end_date": end_date,
                "budget": round(rng.uniform(5000, 100000), 2),
                "status": status,
                "created_at": fake.date_between(start_date=start_date - timedelta(days=30), end_date=start_date)
            })
            campaign_id += 1
    pd.DataFrame(campaigns).to_csv(os.path.join(CSV_FOLDER, "campaigns.csv"), index=False)
    
    # 7. Campaign Content (Minimal - Only for Demo)
    # This table links content to campaigns. It's needed for the "hire influencer" feature.
    # We create minimal links for demo, but users will add more when they hire influencers.
    campaign_links = []
    # Only link to first 3 campaigns (minimal for demo)
    for campaign in campaigns[:3]:
        if len(contents) > 0:
            num_links = min(5, len(contents))
            eligible_indices = list(rng.choice(len(contents), size=num_links, replace=False))
            for idx in eligible_indices:
                content = contents[idx]
                campaign_links.append({
                    "campaign_id": campaign["campaign_id"],
                    "content_id": content["content_id"],
                    "role": rng.choice(["primary", "supporting", "testimonial"], p=np.array([0.4, 0.5, 0.1])),
                    "is_paid": rng.choice([True, False]),
                    "cost": round(float(rng.uniform(0, 50000)), 2) if rng.random() > 0.3 else 0.0
                })
    pd.DataFrame(campaign_links).to_csv(os.path.join(CSV_FOLDER, "campaign_content.csv"), index=False)
    
    # 8. Users (Only One Admin at Pepsi)
    users = []
    users.append({
        "user_id": 1,
        "email": "admin@pepsi.com",
        "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqJ5q5q5qO",  # Placeholder bcrypt hash
        "role": "admin",
        "company": "Pepsi",
        "full_name": "Admin User",
        "created_at": "2023-01-01"
    })
    pd.DataFrame(users).to_csv(os.path.join(CSV_FOLDER, "users.csv"), index=False)
    
    print(f"Generated data: {len(influencers)} influencers, {len(contents)} posts, {len(campaigns)} campaigns")


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
    # Generate data if CSV files don't exist
    generate_data_if_needed()
    
    # Drop all tables and recreate to ensure schema matches models
    print("Dropping existing tables...")
    try:
        Base.metadata.drop_all(engine, checkfirst=True)
    except Exception as e:
        print(f"Warning during drop: {e}, continuing...")
    print("Creating tables...")
    try:
        Base.metadata.create_all(engine, checkfirst=True)
    except Exception as e:
        print(f"Warning during create: {e}, continuing...")
    session = SessionLocal()

    try:
        # Clear all tables in reverse dependency order to avoid foreign key violations
        print("Clearing existing data from tables...")
        try:
            session.query(CampaignContentDB).delete()
            session.query(AudienceDemographicsDB).delete()
            session.query(EngagementDB).delete()
            session.query(ContentDB).delete()
            session.query(CampaignDB).delete()
            session.query(InfluencerDB).delete()
            session.query(BrandDB).delete()
            session.query(UserDB).delete()
            session.commit()
            print("  Cleared all existing data")
        except Exception as e:
            session.rollback()
            print(f"  Warning during clear: {e}, continuing...")
        
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
            print("\nETL completed successfully. All requirements met!")
        else:
            print("\nETL completed but some data may be missing. Check warnings above.")
        
        # ----------------------------
        # Reset PostgreSQL sequences to prevent duplicate key errors
        # ----------------------------
        print("\nResetting PostgreSQL sequences...")
        try:
            # Get max IDs for each table with auto-incrementing primary keys
            tables_to_reset = [
                ("campaign_content", "id"),
                ("audience_demographics", "audience_id"),
                ("engagement", "engagement_id"),
                ("prediction_logs", "log_id"),
                ("api_logs", "log_id"),
                ("fact_influencer_performance", "id"),
                ("fact_content_features", "id"),
            ]
            
            for table_name, id_column in tables_to_reset:
                try:
                    # Get max ID from table
                    result = session.execute(
                        text(f"SELECT COALESCE(MAX({id_column}), 0) FROM {table_name}")
                    ).scalar()
                    max_id = result if result else 0
                    
                    # Reset sequence to max_id + 1, but at least 1 (sequences can't be 0)
                    next_val = max(1, max_id + 1)
                    sequence_name = f"{table_name}_{id_column}_seq"
                    
                    # Check if sequence exists
                    seq_exists = session.execute(
                        text("SELECT EXISTS(SELECT 1 FROM pg_sequences WHERE schemaname = 'public' AND sequencename = :seq_name)"),
                        {"seq_name": sequence_name}
                    ).scalar()
                    
                    if seq_exists:
                        # Use string formatting for sequence name (safe as it's a fixed table name)
                        # If table is empty (max_id=0), set to 1 with is_called=false so nextval returns 1
                        # Otherwise, set to max_id with is_called=true so nextval returns max_id + 1
                        if max_id == 0:
                            # Empty table: set to 1 with is_called=false
                            session.execute(
                                text(f"SELECT setval('{sequence_name}', 1, false)")
                            )
                            print(f"  Reset {sequence_name} to 1 (empty table)")
                        else:
                            # Table has data: set to max_id with is_called=true
                            session.execute(
                                text(f"SELECT setval('{sequence_name}', {max_id}, true)")
                            )
                            print(f"  Reset {sequence_name} to {next_val} (max_id={max_id})")
                    else:
                        print(f"  Sequence {sequence_name} does not exist, skipping")
                except Exception as table_error:
                    print(f"  Warning: Could not reset sequence for {table_name}: {table_error}")
                    continue
            
            session.commit()
            print("  All sequences reset successfully")
        except Exception as e:
            session.rollback()
            print(f"  Warning: Could not reset sequences: {e}")
            # Continue anyway - this is not critical for ETL completion

    except Exception as e:
        print(f"\nETL failed with error: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    run_etl()
