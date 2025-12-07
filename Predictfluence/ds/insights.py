"""
Advanced modeling and analytics utilities for Predictfluence.

Adds:
- Per-influencer "skill" scores (shrunken residuals vs. the regression model).
- Tier classifier (A/B/C) trained directly instead of deriving from regression.
- Unsupervised clustering for influencer segmentation.
- Time-aware posting schedule suggestions (best day/hour from historical data).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from config import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    OUTPUTS_DIR,
    RANDOM_STATE,
    TARGET_COLUMN,
    new_model_version,
)
from modeling import ModelBundle


# ---------------------------------------------------------------------------
# Influencer skill scores
# ---------------------------------------------------------------------------
def estimate_influencer_skill(
    data: pd.DataFrame, bundle: ModelBundle, shrinkage_k: int = 5
) -> pd.DataFrame:
    """
    Estimate influencer-specific performance biases using shrunken residuals.

    Args:
        data: DataFrame with features, influencer_id, and engagement_rate.
        bundle: Trained regression model bundle.
        shrinkage_k: Higher values => stronger shrinkage toward 0 for low-volume influencers.
    Returns:
        DataFrame with influencer_id, n_posts, mean_residual, shrinkage_weight, skill_score.
    """
    if data.empty:
        raise ValueError("No data available to estimate influencer skill scores.")
    if TARGET_COLUMN not in data.columns or "influencer_id" not in data.columns:
        raise ValueError("Data must include influencer_id and engagement_rate.")

    preds = bundle.pipeline.predict(data[FEATURE_COLUMNS])
    residuals = data[TARGET_COLUMN] - preds

    agg = (
        pd.DataFrame({"influencer_id": data["influencer_id"], "residual": residuals})
        .groupby("influencer_id")
        .agg(mean_residual=("residual", "mean"), n_posts=("residual", "count"))
        .reset_index()
    )
    agg["shrinkage_weight"] = agg["n_posts"] / (agg["n_posts"] + shrinkage_k)
    agg["skill_score"] = agg["mean_residual"] * agg["shrinkage_weight"]
    return agg.sort_values("skill_score", ascending=False).reset_index(drop=True)


def save_influencer_skill_scores(
    scores: pd.DataFrame, output_dir: Path = OUTPUTS_DIR, version: Optional[str] = None
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    version = version or new_model_version(prefix="skill")
    path = output_dir / f"influencer_skill_{version}.csv"
    scores.to_csv(path, index=False)
    return path


# ---------------------------------------------------------------------------
# Tier classifier (A/B/C)
# ---------------------------------------------------------------------------
@dataclass
class TierModelBundle:
    pipeline: Pipeline
    version: str
    features: list[str]
    path: Optional[Path] = None


def _build_preprocessor() -> ColumnTransformer:
    """
    Shared preprocessing for classification models.
    """
    numeric_features = [f for f in FEATURE_COLUMNS if f not in CATEGORICAL_FEATURES]

    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        [("categorical", categorical, CATEGORICAL_FEATURES), ("numeric", numeric, numeric_features)]
    )


def assign_tiers(target: pd.Series, high_q: float = 0.9, mid_q: float = 0.6) -> pd.Series:
    """
    Label A/B/C tiers from engagement_rate quantiles.
    """
    if target.empty:
        return pd.Series(dtype=str)
    q_high = target.quantile(high_q)
    q_mid = target.quantile(mid_q)

    def _tier(val: float) -> str:
        if val >= q_high:
            return "A"
        if val >= q_mid:
            return "B"
        return "C"

    return target.apply(_tier)


def train_tier_classifier(
    data: pd.DataFrame, random_state: int = RANDOM_STATE
) -> tuple[TierModelBundle, float, float]:
    """
    Train a direct A/B/C classifier with the existing feature set.
    Returns:
        (bundle, accuracy, macro_f1)
    """
    if data.empty:
        raise ValueError("No data available to train tier classifier.")
    if TARGET_COLUMN not in data.columns:
        raise ValueError(f"Data must include target column '{TARGET_COLUMN}'.")

    tiers = assign_tiers(data[TARGET_COLUMN])
    X = data[FEATURE_COLUMNS]
    y = tiers

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y
    )

    pipeline = Pipeline(
        [
            ("preprocess", _build_preprocessor()),
            ("model", GradientBoostingClassifier(random_state=random_state)),
        ]
    )
    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_val)
    acc = float(accuracy_score(y_val, preds))
    macro_f1 = float(f1_score(y_val, preds, average="macro"))

    version = new_model_version(prefix="tier")
    bundle = TierModelBundle(pipeline=pipeline, version=version, features=FEATURE_COLUMNS)
    return bundle, acc, macro_f1


def save_tier_model(bundle: TierModelBundle, output_dir: Path = OUTPUTS_DIR) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{bundle.version}.joblib"
    joblib.dump(
        {"pipeline": bundle.pipeline, "version": bundle.version, "features": bundle.features},
        path,
    )
    bundle.path = path
    return path


def load_latest_tier_model(output_dir: Path = OUTPUTS_DIR) -> Optional[TierModelBundle]:
    if not output_dir.exists():
        return None
    candidates = sorted(output_dir.glob("tier-*.joblib"))
    if not candidates:
        return None
    latest = candidates[-1]
    payload = joblib.load(latest)
    return TierModelBundle(
        pipeline=payload["pipeline"],
        version=payload["version"],
        features=payload.get("features", FEATURE_COLUMNS),
        path=latest,
    )


def predict_tier(bundle: TierModelBundle, payload: pd.DataFrame) -> pd.Series:
    """
    Predict class labels (A/B/C) for provided rows.
    """
    return pd.Series(bundle.pipeline.predict(payload[bundle.features]), index=payload.index)


# ---------------------------------------------------------------------------
# Unsupervised clustering for influencer segmentation
# ---------------------------------------------------------------------------
def cluster_influencers(
    data: pd.DataFrame,
    n_clusters: int = 5,
    random_state: int = RANDOM_STATE,
) -> tuple[pd.DataFrame, KMeans]:
    """
    Build per-influencer feature vectors and cluster them.
    Returns:
        (DataFrame with influencer_id + cluster label, fitted KMeans)
    """
    required_cols = {"influencer_id", "follower_count", "category", "audience_top_country", TARGET_COLUMN}
    missing = required_cols - set(data.columns)
    if missing:
        raise ValueError(f"Missing columns for clustering: {sorted(missing)}")

    agg = (
        data.groupby("influencer_id").agg(
            follower_count=("follower_count", "mean"),
            tag_count=("tag_count", "mean"),
            caption_length=("caption_length", "mean"),
            engagement_rate=(TARGET_COLUMN, "mean"),
            category=("category", lambda s: s.mode().iloc[0] if not s.mode().empty else "Unknown"),
            audience_top_country=(
                "audience_top_country",
                lambda s: s.mode().iloc[0] if not s.mode().empty else "Unknown",
            ),
            content_type=("content_type", lambda s: s.mode().iloc[0] if not s.mode().empty else "Unknown"),
            n_posts=("content_id", "count") if "content_id" in data.columns else ("influencer_id", "count"),
        )
    ).reset_index()

    cat_cols = ["category", "audience_top_country", "content_type"]
    num_cols = [c for c in agg.columns if c not in cat_cols + ["influencer_id"]]

    encoded = pd.get_dummies(agg[cat_cols], dummy_na=True)
    scaled = agg[num_cols].fillna(0)
    feature_matrix = pd.concat([scaled, encoded], axis=1)

    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(feature_matrix)

    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init="auto")
    clusters = model.fit_predict(features_scaled)

    result = agg[["influencer_id", "n_posts"]].copy()
    result["cluster"] = clusters
    return result, model


# ---------------------------------------------------------------------------
# Time-aware posting schedule
# ---------------------------------------------------------------------------
def _compute_day_hour_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "post_date" in df.columns:
        df["post_date"] = pd.to_datetime(df["post_date"])
        df["day_of_week"] = df["post_date"].dt.day_name()
    if "post_hour" not in df.columns and "post_datetime" in df.columns:
        df["post_datetime"] = pd.to_datetime(df["post_datetime"])
        df["post_hour"] = df["post_datetime"].dt.hour
    return df


def suggest_posting_schedule(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Provide best days/hours to post based on historical engagement_rate.
    Returns dict with 'by_day' and optionally 'by_hour' DataFrames.
    """
    if data.empty:
        raise ValueError("No data available for schedule suggestions.")
    if TARGET_COLUMN not in data.columns:
        raise ValueError(f"Data must include target column '{TARGET_COLUMN}'.")

    df = _compute_day_hour_columns(data)

    by_day = None
    if "day_of_week" in df.columns:
        by_day = (
            df.groupby("day_of_week")[TARGET_COLUMN]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
            .rename(columns={TARGET_COLUMN: "avg_engagement_rate"})
        )

    by_hour = None
    if "post_hour" in df.columns:
        by_hour = (
            df.groupby("post_hour")[TARGET_COLUMN]
            .mean()
            .sort_values(ascending=False)
            .reset_index()
            .rename(columns={TARGET_COLUMN: "avg_engagement_rate"})
        )

    return {"by_day": by_day, "by_hour": by_hour}


def save_schedule(schedule: dict[str, pd.DataFrame], output_dir: Path = OUTPUTS_DIR) -> dict[str, Optional[Path]]:
    output_dir.mkdir(parents=True, exist_ok=True)
    version = new_model_version(prefix="schedule")
    paths: dict[str, Optional[Path]] = {"by_day": None, "by_hour": None}

    if schedule.get("by_day") is not None:
        paths["by_day"] = output_dir / f"schedule_by_day_{version}.csv"
        schedule["by_day"].to_csv(paths["by_day"], index=False)
    if schedule.get("by_hour") is not None:
        paths["by_hour"] = output_dir / f"schedule_by_hour_{version}.csv"
        schedule["by_hour"].to_csv(paths["by_hour"], index=False)
    return paths
