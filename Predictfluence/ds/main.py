"""
Predictfluence DS service.

Provides lightweight training and prediction endpoints that use the shared
PostgreSQL database. Falls back to synthetic data when the database does not
have enough rows to train a baseline model.
"""

from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sqlalchemy.orm import Session

from Database.database import create_tables, get_db
from Database.models import (
    ContentDB,
    FactContentFeaturesDB,
    FactInfluencerPerformanceDB,
    PredictionLogDB,
)

app = FastAPI(title="Predictfluence DS Service", version="0.1.0")


class TrainResponse(BaseModel):
    n_rows: int
    used_synthetic: bool
    r2: Optional[float]
    mae: Optional[float]
    model_version: str
    features: list[str]


class PredictRequest(BaseModel):
    follower_count: int
    tag_count: int
    caption_length: int
    content_type: str
    content_id: Optional[int] = None
    influencer_id: Optional[int] = None


class PredictResponse(BaseModel):
    predicted_engagement_rate: float
    model_version: str
    logged: bool


class ModelBundle:
    """
    In-memory model artifact container to keep the FastAPI handlers simple.
    """

    def __init__(self, pipeline: Pipeline, version: str, features: list[str]):
        self.pipeline = pipeline
        self.version = version
        self.features = features


model_bundle: Optional[ModelBundle] = None


def fetch_training_data(db: Session) -> pd.DataFrame:
    """
    Pull training data from the DB by joining fact tables.
    """
    rows = (
        db.query(
            FactContentFeaturesDB.content_id,
            FactContentFeaturesDB.tag_count,
            FactContentFeaturesDB.caption_length,
            FactContentFeaturesDB.content_type,
            FactContentFeaturesDB.engagement_rate,
            FactInfluencerPerformanceDB.follower_count,
        )
        .join(
            FactInfluencerPerformanceDB,
            FactContentFeaturesDB.influencer_id == FactInfluencerPerformanceDB.influencer_id,
        )
        .all()
    )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(
        rows,
        columns=[
            "content_id",
            "tag_count",
            "caption_length",
            "content_type",
            "engagement_rate",
            "follower_count",
        ],
    )


def simulate_training_data(n_rows: int = 200) -> pd.DataFrame:
    """
    Create synthetic training data to allow the DS service to run in isolation.
    """
    rng = np.random.default_rng(seed=42)
    content_types = ["Image", "Video", "Reel", "Story"]

    follower_count = rng.lognormal(mean=10, sigma=0.8, size=n_rows).astype(int)
    tag_count = rng.poisson(lam=3, size=n_rows)
    caption_length = rng.integers(20, 220, size=n_rows)
    content_type = rng.choice(content_types, size=n_rows, p=[0.35, 0.35, 0.2, 0.1])

    base_rate = 0.5 / np.sqrt(np.maximum(follower_count, 1))
    engagement_rate = (
        base_rate
        + 0.002 * tag_count
        + 0.0008 * caption_length
        + rng.normal(loc=0.0, scale=0.05, size=n_rows)
    )
    engagement_rate = np.clip(engagement_rate, 0.0, None)

    return pd.DataFrame(
        {
            "content_id": np.arange(1, n_rows + 1),
            "tag_count": tag_count,
            "caption_length": caption_length,
            "content_type": content_type,
            "engagement_rate": engagement_rate,
            "follower_count": follower_count,
        }
    )


def train_baseline_model(data: pd.DataFrame) -> tuple[ModelBundle, float, float]:
    """
    Train a simple baseline regression model that predicts engagement_rate.
    """
    feature_cols = ["follower_count", "tag_count", "caption_length", "content_type"]
    target_col = "engagement_rate"

    X = data[feature_cols]
    y = data[target_col]

    preprocessor = ColumnTransformer(
        [("content_type", OneHotEncoder(handle_unknown="ignore"), ["content_type"])],
        remainder="passthrough",
    )
    pipeline = Pipeline(
        [
            ("preprocess", preprocessor),
            ("model", LinearRegression()),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)

    r2 = float(r2_score(y_test, preds))
    mae = float(mean_absolute_error(y_test, preds))

    version = datetime.utcnow().strftime("baseline-%Y%m%d%H%M%S")
    bundle = ModelBundle(pipeline=pipeline, version=version, features=feature_cols)
    return bundle, r2, mae


@app.on_event("startup")
def startup_event():
    """
    Ensure tables exist and warm up the model with synthetic data so
    predictions work immediately.
    """
    create_tables()

    global model_bundle
    synthetic_data = simulate_training_data(200)
    model_bundle, _, _ = train_baseline_model(synthetic_data)


@app.get("/health")
def healthcheck():
    return {"status": "ok", "model_ready": model_bundle is not None}


@app.post("/train", response_model=TrainResponse)
def train(db: Session = Depends(get_db)):
    """
    Train the baseline model using DB data when available, otherwise synthetic data.
    """
    global model_bundle

    df = fetch_training_data(db)
    used_synthetic = False

    if df.empty or len(df) < 40:
        df = simulate_training_data(300)
        used_synthetic = True

    model_bundle, r2, mae = train_baseline_model(df)

    return TrainResponse(
        n_rows=len(df),
        used_synthetic=used_synthetic,
        r2=r2,
        mae=mae,
        model_version=model_bundle.version,
        features=model_bundle.features,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, db: Session = Depends(get_db)):
    """
    Generate an engagement_rate prediction. If the model has not been trained
    yet, train once on synthetic data to keep the API responsive.
    """
    global model_bundle

    if model_bundle is None:
        synthetic = simulate_training_data(300)
        model_bundle, _, _ = train_baseline_model(synthetic)

    features = pd.DataFrame(
        [
            {
                "follower_count": payload.follower_count,
                "tag_count": payload.tag_count,
                "caption_length": payload.caption_length,
                "content_type": payload.content_type,
            }
        ]
    )

    pred = float(model_bundle.pipeline.predict(features)[0])

    logged = False
    content_id = payload.content_id
    influencer_id = payload.influencer_id

    # Only log when we can verify the content row exists to avoid FK violations.
    if content_id:
        content = db.query(ContentDB).filter(ContentDB.content_id == content_id).first()
        if content:
            influencer_id = influencer_id or content.influencer_id
            db.add(
                PredictionLogDB(
                    timestamp=datetime.utcnow(),
                    content_id=content_id,
                    influencer_id=influencer_id or content.influencer_id,
                    predicted_engagement=pred,
                    model_version=model_bundle.version,
                )
            )
            db.commit()
            logged = True

    return PredictResponse(
        predicted_engagement_rate=pred,
        model_version=model_bundle.version,
        logged=logged,
    )
