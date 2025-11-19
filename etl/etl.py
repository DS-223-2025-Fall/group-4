import pandas as pd
from loguru import logger
from Database.models import InfluencerDB, ContentDB, EngagementDB
from Database.database import engine, Base, SessionLocal
from Database.data_generator import generate_influencer, generate_content, generate_engagement

from sklearn.linear_model import LinearRegression
import numpy as np

# ---------------------------------------------------------
# STEP 1 — Create tables
# ---------------------------------------------------------
logger.info("Creating tables...")
Base.metadata.create_all(engine)


# ---------------------------------------------------------
# STEP 2 — Simulate Data
# ---------------------------------------------------------
def simulate_all(n_influencers=30, n_content_per_inf=3):
    logger.info("Simulating dataset...")

    influencers = []
    content = []
    engagement = []

    content_id = 1
    engagement_id = 1

    for i in range(1, n_influencers + 1):
        inf = generate_influencer(i)
        influencers.append(inf)

        # generate content + engagement
        for _ in range(n_content_per_inf):
            cont = generate_content(content_id, i)
            content.append(cont)

            eng = generate_engagement(engagement_id, content_id)
            engagement.append(eng)

            content_id += 1
            engagement_id += 1

    return (
        pd.DataFrame(influencers),
        pd.DataFrame(content),
        pd.DataFrame(engagement)
    )


influencers_df, content_df, engagement_df = simulate_all()

# Save CSVs
influencers_df.to_csv("data/influencers.csv", index=False)
content_df.to_csv("data/content.csv", index=False)
engagement_df.to_csv("data/engagement.csv", index=False)

logger.info("Saved CSV files to /data/")


# ---------------------------------------------------------
# STEP 3 — Load into DB
# ---------------------------------------------------------
def load_table(df, table_name):
    df.to_sql(table_name, con=engine, if_exists="append", index=False)
    logger.info(f"Loaded {len(df)} rows into {table_name}")


load_table(influencers_df, "influencers")
load_table(content_df, "content")
load_table(engagement_df, "engagement")


# ---------------------------------------------------------
# STEP 4 — Read sample data (CRUD demonstration)
# ---------------------------------------------------------
logger.info("Reading sample influencers...")

session = SessionLocal()
sample = session.query(InfluencerDB).limit(5).all()

for s in sample:
    logger.info(f"{s.influencer_id}: {s.name} ({s.platform})")


# ---------------------------------------------------------
# STEP 5 — Baseline Model
# ---------------------------------------------------------
logger.info("Training baseline model...")

# merge content + engagement
merged = content_df.merge(
    engagement_df,
    left_on="content_id",
    right_on="content_id",
    how="left"
)

# simple baseline prediction of engagement from views
X = merged[["views"]].values
y = merged["engagement_rate"].values

model = LinearRegression()
model.fit(X, y)

logger.info(f"Coefficient: {model.coef_[0]}")
logger.info(f"Intercept: {model.intercept_}")
logger.info("Baseline model trained!")


logger.info("=== DS ETL Pipeline Completed Successfully ===")