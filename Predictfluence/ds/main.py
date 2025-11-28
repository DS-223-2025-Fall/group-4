"""
Predictfluence DS service.

Provides training and prediction endpoints backed by a shared PostgreSQL DB.
"""

from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Database.database import create_tables, get_db
from Database.models import (
    ContentDB,
    FactInfluencerPerformanceDB,
    PredictionLogDB,
)
from config import MIN_TRAINING_ROWS
from train import (
    FEATURE_COLUMNS,
    ModelBundle,
    load_latest_model,
    load_training_data_from_db,
    save_feature_importance,
    save_model,
    simulate_training_data,
    train_model,
)

app = FastAPI(title="Predictfluence DS Service", version="0.1.0")


class TrainResponse(BaseModel):
    n_rows: int
    used_synthetic: bool
    r2: Optional[float]
    mae: Optional[float]
    model_version: str
    features: list[str]
    top_features: list[str]


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


model_bundle: Optional[ModelBundle] = None


@app.on_event("startup")
def startup_event():
    """
    Ensure tables exist and warm the in-memory model from disk or synthetic data.
    """
    create_tables()

    _load_or_initialize_model()


@app.get("/health")
def healthcheck() -> dict[str, bool]:
    return {"status": "ok", "model_ready": model_bundle is not None}


@app.post("/train", response_model=TrainResponse)
def train(db: Session = Depends(get_db)) -> TrainResponse:
    """
    Train the model using DB data when available, otherwise synthetic data.
    """
    df = load_training_data_from_db(db)
    used_synthetic = False

    if len(df) < MIN_TRAINING_ROWS:
        df = simulate_training_data(400)
        used_synthetic = True

    bundle, r2, mae = train_model(df)
    save_model(bundle)
    importance_df = save_feature_importance(bundle)
    top_features = importance_df.head(5)["feature"].tolist() if not importance_df.empty else []

    _set_model_bundle(bundle)

    return TrainResponse(
        n_rows=len(df),
        used_synthetic=used_synthetic,
        r2=r2,
        mae=mae,
        model_version=bundle.version,
        features=bundle.features,
        top_features=top_features,
    )


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest, db: Session = Depends(get_db)) -> PredictResponse:
    """
    Generate an engagement_rate prediction. If the model has not been trained
    yet, train once on synthetic data to keep the API responsive.
    """
    bundle = _load_or_initialize_model()
    feature_values = build_feature_row(payload, db, bundle.features)
    pred = float(bundle.pipeline.predict(feature_values)[0])

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
                    model_version=bundle.version,
                )
            )
            db.commit()
            logged = True

    return PredictResponse(
        predicted_engagement_rate=pred,
        model_version=bundle.version,
        logged=logged,
    )


def build_feature_row(payload: PredictRequest, db: Session, feature_order: list[str]) -> pd.DataFrame:
    """
    Construct a single-row DataFrame in the expected feature order, enriching
    with DB attributes when available.
    """
    category = None
    audience_top_country = None
    follower_count = payload.follower_count

    if payload.influencer_id:
        perf = (
            db.query(FactInfluencerPerformanceDB)
            .filter(FactInfluencerPerformanceDB.influencer_id == payload.influencer_id)
            .first()
        )
        if perf:
            follower_count = payload.follower_count or perf.follower_count
            category = perf.category
            audience_top_country = perf.audience_top_country

    row = {
        "follower_count": follower_count,
        "tag_count": payload.tag_count,
        "caption_length": payload.caption_length,
        "content_type": payload.content_type,
        "category": category or "Unknown",
        "audience_top_country": audience_top_country or "Unknown",
    }

    return pd.DataFrame([row], columns=feature_order or FEATURE_COLUMNS)


def _load_or_initialize_model() -> ModelBundle:
    """
    Load the latest model from disk, or train on synthetic data if none exist.
    """
    global model_bundle

    latest = load_latest_model()
    if latest and (model_bundle is None or latest.version != model_bundle.version):
        model_bundle = latest

    if model_bundle is None:
        synthetic = simulate_training_data(400)
        model_bundle, _, _ = train_model(synthetic)
        save_model(model_bundle)

    return model_bundle


def _set_model_bundle(bundle: ModelBundle) -> None:
    """
    Update the global model bundle reference.
    """
    global model_bundle
    model_bundle = bundle
