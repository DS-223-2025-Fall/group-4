import os
import pandas as pd
from pydantic import BaseModel
from typing import Optional
from database import DBHelper
from models import ALL_TABLES
import dotenv
from datetime import datetime
import random
import numpy as np

dotenv.load_dotenv()

random.seed(42)
np.random.seed(42)

# ----------------------------
# CSV folder
# ----------------------------
CSV_FOLDER = os.getenv("CSV_FOLDER", "csv_data")
os.makedirs(CSV_FOLDER, exist_ok=True)

# ----------------------------
# TABLE SCHEMAS
# ----------------------------
TABLE_SCHEMAS = {
    "influencers": [
        ("influencer_id", "SERIAL PRIMARY KEY"),
        ("name", "VARCHAR"),
        ("username", "VARCHAR"),
        ("platform", "VARCHAR"),
        ("follower_count", "INT"),
        ("category", "VARCHAR"),
        ("created_at", "TIMESTAMP")
    ],
    "content": [
        ("content_id", "SERIAL PRIMARY KEY"),
        ("influencer_id", "INT"),
        ("content_type", "VARCHAR"),
        ("topic", "VARCHAR"),
        ("post_date", "DATE"),
        ("caption", "TEXT"),
        ("url", "VARCHAR")
    ],
    "engagement": [
        ("engagement_id", "SERIAL PRIMARY KEY"),
        ("content_id", "INT"),
        ("likes", "INT"),
        ("comments", "INT"),
        ("shares", "INT"),
        ("views", "INT"),
        ("engagement_rate", "FLOAT")
    ],
    "audience_demographics": [
        ("audience_id", "SERIAL PRIMARY KEY"),
        ("influencer_id", "INT"),
        ("age_group", "VARCHAR"),
        ("gender", "VARCHAR"),
        ("country", "VARCHAR"),
        ("percentage", "FLOAT")
    ],
    "fact_influencer_performance": [
        ("id", "SERIAL PRIMARY KEY"),
        ("influencer_id", "INT"),
        ("avg_engagement_rate", "FLOAT"),
        ("avg_likes", "FLOAT"),
        ("avg_comments", "FLOAT"),
        ("avg_shares", "FLOAT"),
        ("avg_views", "FLOAT"),
        ("follower_count", "INT"),
        ("category", "VARCHAR"),
        ("audience_top_country", "VARCHAR")
    ],
    "fact_content_features": [
        ("id", "SERIAL PRIMARY KEY"),
        ("content_id", "INT"),
        ("influencer_id", "INT"),
        ("tag_count", "INT"),
        ("caption_length", "INT"),
        ("content_type", "VARCHAR"),
        ("engagement_rate", "FLOAT")
    ],
    "brands": [
        ("brand_id", "SERIAL PRIMARY KEY"),
        ("name", "VARCHAR"),
        ("industry", "VARCHAR"),
        ("country", "VARCHAR"),
        ("created_at", "TIMESTAMP")
    ],
    "campaigns": [
        ("campaign_id", "SERIAL PRIMARY KEY"),
        ("brand_id", "INT"),
        ("name", "VARCHAR"),
        ("objective", "VARCHAR"),
        ("start_date", "DATE"),
        ("end_date", "DATE"),
        ("budget", "FLOAT"),
        ("status", "VARCHAR"),
        ("created_at", "TIMESTAMP")
    ],
    "campaign_content": [
        ("id", "SERIAL PRIMARY KEY"),
        ("campaign_id", "INT"),
        ("content_id", "INT"),
        ("role", "VARCHAR"),
        ("is_paid", "BOOLEAN")
    ],
    "prediction_logs": [
        ("log_id", "SERIAL PRIMARY KEY"),
        ("timestamp", "TIMESTAMP"),
        ("content_id", "INT"),
        ("influencer_id", "INT"),
        ("predicted_engagement", "FLOAT"),
        ("model_version", "VARCHAR")
    ],
    "api_logs": [
        ("log_id", "SERIAL PRIMARY KEY"),
        ("user", "VARCHAR"),
        ("endpoint", "VARCHAR"),
        ("status", "VARCHAR"),
        ("timestamp", "TIMESTAMP")
    ]
}

# ----------------------------
# Connect to DB
# ----------------------------
db = DBHelper()
cur = db.conn.cursor()

# ----------------------------
# DROP TABLES IF EXIST (reverse order for FKs)
# ----------------------------
for table in reversed(ALL_TABLES):
    cur.execute(f'DROP TABLE IF EXISTS "{table.table_name}" CASCADE;')
db.conn.commit()

# ----------------------------
# CREATE TABLES DYNAMICALLY
# ----------------------------
def create_table_sql(table):
    sql_cols = []
    for col_name, col_type in TABLE_SCHEMAS[table.table_name]:
        sql_cols.append(f'"{col_name}" {col_type}')

    # Add foreign keys if any
    if hasattr(table, "foreign_keys"):
        for fk_col, ref in table.foreign_keys.items():
            table_ref, col_ref = ref.split(".")
            sql_cols.append(
                f'FOREIGN KEY ("{fk_col}") REFERENCES "{table_ref}"("{col_ref}") ON DELETE CASCADE'
            )

    sql = f'CREATE TABLE IF NOT EXISTS "{table.table_name}" (\n    {",\n    ".join(sql_cols)}\n);'
    return sql

for table in ALL_TABLES:
    sql = create_table_sql(table)
    cur.execute(sql)
db.conn.commit()

# ----------------------------
# Pydantic models for CSV validation
# ----------------------------
class InfluencerModel(BaseModel):
    influencer_id: Optional[int]
    name: str
    username: str
    platform: str
    follower_count: int
    category: str
    created_at: Optional[datetime]

class ContentModel(BaseModel):
    content_id: Optional[int]
    influencer_id: int
    content_type: str
    topic: str
    post_date: Optional[datetime]
    caption: Optional[str]
    url: Optional[str]

class EngagementModel(BaseModel):
    engagement_id: Optional[int]
    content_id: int
    likes: Optional[int] = 0
    comments: Optional[int] = 0
    shares: Optional[int] = 0
    views: Optional[int] = 0
    engagement_rate: Optional[float] = 0.0

class AudienceDemographicsModel(BaseModel):
    audience_id: Optional[int]
    influencer_id: int
    age_group: Optional[str]
    gender: Optional[str]
    country: Optional[str]
    percentage: Optional[float] = 0.0

# ----------------------------
# Load CSVs dynamically
# ----------------------------
def load_csv_to_table(table_name, csv_file, model_class):
    path = os.path.join(CSV_FOLDER, csv_file)
    if not os.path.exists(path):
        print(f"CSV not found: {path}, skipping")
        return

    df = pd.read_csv(path)

    # Parse dates correctly
    for col in df.columns:
        if "date" in col or "timestamp" in col or "created_at" in col:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    auto_pk_cols = [
        field_name
        for field_name in model_class.model_fields
        if field_name.endswith("_id") and field_name not in ["influencer_id", "content_id", "audience_id"]
    ]

    # Iterate rows
    for _, row in df.iterrows():
        validated = model_class(**row.to_dict())

        columns = [f for f in model_class.model_fields if f not in auto_pk_cols]

        placeholders = ",".join(["%s"] * len(columns))
        sql = f'INSERT INTO "{table_name}" ({",".join(columns)}) VALUES ({placeholders})'

        values = tuple(getattr(validated, f) for f in columns)
        cur.execute(sql, values)

    db.conn.commit()

# ----------------------------
# Load CSVs
# ----------------------------
load_csv_to_table("influencers", "influencers.csv", InfluencerModel)
load_csv_to_table("content", "content.csv", ContentModel)
load_csv_to_table("engagement", "engagement.csv", EngagementModel)
load_csv_to_table("audience_demographics", "audience_demographics.csv", AudienceDemographicsModel)

# ----------------------------
# Populate fact tables
# ----------------------------
# fact_influencer_performance
cur.execute(
    """
INSERT INTO fact_influencer_performance (influencer_id, avg_engagement_rate, avg_likes, avg_comments, avg_shares, avg_views, follower_count, category, audience_top_country)
SELECT
    i.influencer_id,
    COALESCE(AVG(e.engagement_rate),0),
    COALESCE(AVG(e.likes),0),
    COALESCE(AVG(e.comments),0),
    COALESCE(AVG(e.shares),0),
    COALESCE(AVG(e.views),0),
    i.follower_count,
    i.category,
    (SELECT country FROM audience_demographics ad WHERE ad.influencer_id=i.influencer_id ORDER BY percentage DESC LIMIT 1)
FROM influencers i
LEFT JOIN content c ON i.influencer_id = c.influencer_id
LEFT JOIN engagement e ON c.content_id = e.content_id
GROUP BY i.influencer_id;
"""
)
db.conn.commit()

# fact_content_features
cur.execute(
    """
INSERT INTO fact_content_features (content_id, influencer_id, tag_count, caption_length, content_type, engagement_rate)
SELECT
    c.content_id,
    c.influencer_id,
    0,
    LENGTH(c.caption),
    c.content_type,
    COALESCE(e.engagement_rate,0)
FROM content c
LEFT JOIN engagement e ON c.content_id = e.content_id;
"""
)
db.conn.commit()

# ----------------------------
# Populate campaign_content deterministically
# ----------------------------
campaigns = db.query("SELECT campaign_id FROM campaigns")
contents = db.query("SELECT content_id, influencer_id FROM content")

data_to_insert = []
for campaign in campaigns:
    for content in contents:
        if (campaign["campaign_id"] + content["influencer_id"]) % 3 == 0:
            role = ["primary", "supporting"][(content["content_id"] + campaign["campaign_id"]) % 2]
            is_paid = ((content["content_id"] + campaign["campaign_id"]) % 2 == 0)
            data_to_insert.append((campaign["campaign_id"], content["content_id"], role, is_paid))

sql = """
INSERT INTO campaign_content (campaign_id, content_id, role, is_paid)
VALUES (%s, %s, %s, %s)
"""
db.execute_many(sql, data_to_insert)

# ----------------------------
# Close connections
# ----------------------------
cur.close()
db.close()
print("Database setup complete")
