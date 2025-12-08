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
from config import MIN_TRAINING_ROWS, new_model_version
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
from insights import (
    cluster_influencers,
    estimate_influencer_skill,
    load_latest_tier_model,
    predict_tier,
    save_influencer_skill_scores,
    save_schedule,
    save_tier_model,
    suggest_posting_schedule,
    train_tier_classifier,
)
from batch_scoring import run_batch_scoring

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


class SkillScoresResponse(BaseModel):
    influencer_id: int
    n_posts: int
    mean_residual: float
    shrinkage_weight: float
    skill_score: float


class SkillScoresListResponse(BaseModel):
    scores: list[dict]
    model_version: str


class TierPredictRequest(BaseModel):
    follower_count: int
    tag_count: int
    caption_length: int
    content_type: str
    category: Optional[str] = None
    audience_top_country: Optional[str] = None


class TierPredictResponse(BaseModel):
    tier: str
    model_version: str


class TierTrainResponse(BaseModel):
    model_version: str
    accuracy: float
    macro_f1: float
    n_rows: int


class ClusterResponse(BaseModel):
    influencer_id: int
    cluster: int
    n_posts: int


class ClusterListResponse(BaseModel):
    clusters: list[dict]
    n_clusters: int


class ScheduleResponse(BaseModel):
    by_day: Optional[list[dict]] = None
    by_hour: Optional[list[dict]] = None
    model_version: str


class BatchScoringResponse(BaseModel):
    output_path: str
    n_predictions: int
    model_version: str
    segments: dict[str, int]


model_bundle: Optional[ModelBundle] = None


@app.on_event("startup")
def startup_event():
    """
    Ensure tables exist and warm the in-memory model from disk or synthetic data.
    Auto-train model if database has sufficient data.
    """
    import time
    
    create_tables()

    # Wait for ETL to complete, retry up to 30 seconds
    max_retries = 6
    retry_delay = 5
    df = None
    
    for attempt in range(max_retries):
        db = next(get_db())
        try:
            df = load_training_data_from_db(db)
            if len(df) >= MIN_TRAINING_ROWS:
                break
            if attempt < max_retries - 1:
                print(f"Waiting for ETL data... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Database not ready yet: {e}, retrying...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to load data: {e}, using synthetic model")
                _load_or_initialize_model()
                return
        finally:
            db.close()
    
    # Auto-train model if we have real data
    if df is not None and len(df) >= MIN_TRAINING_ROWS:
        print(f"Auto-training model with {len(df)} rows from database...")
        try:
            bundle, r2, mae = train_model(df)
            save_model(bundle)
            save_feature_importance(bundle)
            _set_model_bundle(bundle)
            print(f"Model trained: R²={r2:.3f}, MAE={mae:.3f}, version={bundle.version}")
        except Exception as e:
            print(f"Training failed: {e}, using synthetic model")
            _load_or_initialize_model()
    else:
        print(f"Only {len(df) if df is not None else 0} rows available, using synthetic model")
        _load_or_initialize_model()


@app.get("/health")
def healthcheck() -> dict[str, object]:
    """
    Return service health; use a broad return type to match the mixed value types.
    """
    return {"status": "ok", "model_ready": bool(model_bundle is not None)}


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


# ---------------------------------------------------------------------------
# Advanced Analytics Endpoints
# ---------------------------------------------------------------------------
@app.post("/insights/skill-scores", response_model=SkillScoresListResponse)
def get_skill_scores(db: Session = Depends(get_db)) -> SkillScoresListResponse:
    """
    Compute and return influencer skill scores based on model residuals.
    """
    bundle = _load_or_initialize_model()
    df = load_training_data_from_db(db)
    
    if len(df) < MIN_TRAINING_ROWS:
        df = simulate_training_data(400)
    
    if "influencer_id" not in df.columns:
        raise HTTPException(status_code=400, detail="Data must include influencer_id")
    
    scores_df = estimate_influencer_skill(df, bundle)
    path = save_influencer_skill_scores(scores_df)
    
    return SkillScoresListResponse(
        scores=scores_df.to_dict(orient="records"),
        model_version=bundle.version
    )


@app.post("/insights/tier/predict", response_model=TierPredictResponse)
def predict_tier_endpoint(payload: TierPredictRequest, db: Session = Depends(get_db)) -> TierPredictResponse:
    """
    Predict content tier (A/B/C) for a single content piece.
    """
    tier_bundle = load_latest_tier_model()
    
    # Train tier model if it doesn't exist
    if tier_bundle is None:
        df = load_training_data_from_db(db)
        if len(df) < MIN_TRAINING_ROWS:
            df = simulate_training_data(400)
        
        tier_bundle, _, _ = train_tier_classifier(df)
        save_tier_model(tier_bundle)
    
    feature_row = pd.DataFrame([{
        "follower_count": payload.follower_count,
        "tag_count": payload.tag_count,
        "caption_length": payload.caption_length,
        "content_type": payload.content_type,
        "category": payload.category or "Unknown",
        "audience_top_country": payload.audience_top_country or "Unknown",
    }], columns=FEATURE_COLUMNS)
    
    tier = predict_tier(tier_bundle, feature_row).iloc[0]
    
    return TierPredictResponse(
        tier=tier,
        model_version=tier_bundle.version
    )


@app.post("/insights/tier/train", response_model=TierTrainResponse)
def train_tier_endpoint(db: Session = Depends(get_db)) -> TierTrainResponse:
    """
    Train the tier classifier model.
    """
    df = load_training_data_from_db(db)
    used_synthetic = False
    
    if len(df) < MIN_TRAINING_ROWS:
        df = simulate_training_data(400)
        used_synthetic = True
    
    tier_bundle, accuracy, macro_f1 = train_tier_classifier(df)
    save_tier_model(tier_bundle)
    
    return TierTrainResponse(
        model_version=tier_bundle.version,
        accuracy=accuracy,
        macro_f1=macro_f1,
        n_rows=len(df)
    )


@app.post("/insights/clusters", response_model=ClusterListResponse)
def get_clusters(
    n_clusters: int = 5,
    db: Session = Depends(get_db)
) -> ClusterListResponse:
    """
    Cluster influencers using KMeans for segmentation.
    """
    df = load_training_data_from_db(db)
    
    if len(df) < MIN_TRAINING_ROWS:
        df = simulate_training_data(400)
    
    # Ensure we have required columns
    if "content_id" not in df.columns:
        df["content_id"] = df.index + 1
    
    clusters_df, _ = cluster_influencers(df, n_clusters=n_clusters)
    
    return ClusterListResponse(
        clusters=clusters_df.to_dict(orient="records"),
        n_clusters=n_clusters
    )


@app.get("/insights/posting-schedule", response_model=ScheduleResponse)
def get_posting_schedule(db: Session = Depends(get_db)) -> ScheduleResponse:
    """
    Get optimal posting schedule based on historical engagement patterns.
    """
    df = load_training_data_from_db(db)
    
    if len(df) < MIN_TRAINING_ROWS:
        df = simulate_training_data(400)
    
    schedule = suggest_posting_schedule(df)
    paths = save_schedule(schedule)
    version = new_model_version(prefix="schedule")
    
    by_day = schedule.get("by_day")
    by_hour = schedule.get("by_hour")
    
    return ScheduleResponse(
        by_day=by_day.to_dict(orient="records") if by_day is not None else None,
        by_hour=by_hour.to_dict(orient="records") if by_hour is not None else None,
        model_version=version
    )


@app.post("/batch-score")
def batch_score_endpoint(db: Session = Depends(get_db)) -> BatchScoringResponse:
    """
    Run batch scoring on all available data and return predictions with segments.
    """
    try:
        # Check if we have data
        df = load_training_data_from_db(db)
        if len(df) < MIN_TRAINING_ROWS:
            df = simulate_training_data(400)
            # For synthetic data, we need to save it temporarily or use it directly
            # For now, we'll use the model to score the synthetic data
            bundle = _load_or_initialize_model()
            if df.empty:
                raise HTTPException(status_code=400, detail="No data available for batch scoring")
            
            # Score synthetic data
            preds = bundle.pipeline.predict(df[FEATURE_COLUMNS])
            pred_series = pd.Series(preds, name="predicted_engagement_rate")
            
            # Import segmentation function
            from batch_scoring import assign_segments
            segments_series = assign_segments(pred_series)
            
            results_df = pd.DataFrame({
                "content_id": df.get("content_id", range(len(df))),
                "influencer_id": df.get("influencer_id", range(len(df))),
                "predicted_engagement_rate": pred_series,
                "segment": segments_series,
                "model_version": bundle.version,
            })
            
            # Save to outputs
            from config import OUTPUTS_DIR
            OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
            output_path = OUTPUTS_DIR / f"batch_predictions_{bundle.version}.csv"
            results_df.to_csv(output_path, index=False)
        else:
            output_path = run_batch_scoring(db=db)
            results_df = pd.read_csv(output_path)
        
        segments = results_df["segment"].value_counts().to_dict()
        bundle = load_latest_model()
        version = bundle.version if bundle else "unknown"
        
        return BatchScoringResponse(
            output_path=str(output_path),
            n_predictions=len(results_df),
            model_version=version,
            segments=segments
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch scoring failed: {str(e)}")
