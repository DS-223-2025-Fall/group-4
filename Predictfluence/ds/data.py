"""
Data loading and simulation utilities for Predictfluence DS.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from Database.models import FactContentFeaturesDB, FactInfluencerPerformanceDB
from config import FEATURE_COLUMNS, TARGET_COLUMN


def load_training_data_from_db(db: Session) -> pd.DataFrame:
    """
    Pull training data by joining fact_content_features with fact_influencer_performance.
    """
    rows = (
        db.query(
            FactContentFeaturesDB.content_id,
            FactContentFeaturesDB.influencer_id,
            FactContentFeaturesDB.tag_count,
            FactContentFeaturesDB.caption_length,
            FactContentFeaturesDB.content_type,
            FactContentFeaturesDB.engagement_rate,
            FactInfluencerPerformanceDB.follower_count,
            FactInfluencerPerformanceDB.category,
            FactInfluencerPerformanceDB.audience_top_country,
        )
        .join(
            FactInfluencerPerformanceDB,
            FactContentFeaturesDB.influencer_id == FactInfluencerPerformanceDB.influencer_id,
        )
        .all()
    )

    if not rows:
        return pd.DataFrame(columns=["content_id", "influencer_id", *FEATURE_COLUMNS, TARGET_COLUMN])

    return pd.DataFrame(
        rows,
        columns=[
            "content_id",
            "influencer_id",
            "tag_count",
            "caption_length",
            "content_type",
            TARGET_COLUMN,
            "follower_count",
            "category",
            "audience_top_country",
        ],
    )


def simulate_training_data(n_rows: int = 400, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic training data aligned with the DB schema to keep the
    service functional when the DB is sparse.
    """
    rng = np.random.default_rng(seed=seed)
    content_types = ["Image", "Video", "Reel", "Story"]
    categories = ["Beauty", "Fitness", "Tech", "Food", "Travel", "Gaming"]
    countries = ["USA", "UK", "Canada", "Germany", "France", "India", "Brazil"]

    follower_count = rng.lognormal(mean=10, sigma=0.8, size=n_rows).astype(int)
    tag_count = rng.poisson(lam=3, size=n_rows)
    caption_length = rng.integers(20, 240, size=n_rows)
    content_type = rng.choice(content_types, size=n_rows, p=[0.35, 0.35, 0.2, 0.1])
    category = rng.choice(categories, size=n_rows)
    audience_top_country = rng.choice(countries, size=n_rows)

    base_rate = 0.6 / np.sqrt(np.maximum(follower_count, 1))
    engagement_rate = (
        base_rate
        + 0.003 * tag_count
        + 0.0009 * caption_length
        + rng.normal(loc=0.0, scale=0.04, size=n_rows)
    )
    engagement_rate = np.clip(engagement_rate, 0.0, None)

    return pd.DataFrame(
        {
            "content_id": np.arange(1, n_rows + 1),
            "influencer_id": np.arange(1, n_rows + 1),
            "tag_count": tag_count,
            "caption_length": caption_length,
            "content_type": content_type,
            TARGET_COLUMN: engagement_rate,
            "follower_count": follower_count,
            "category": category,
            "audience_top_country": audience_top_country,
        }
    )
