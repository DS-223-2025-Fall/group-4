"""
Modeling utilities for Predictfluence DS.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import joblib
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from config import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    MODELS_DIR,
    NUMERIC_FEATURES,
    OUTPUTS_DIR,
    RANDOM_STATE,
    TARGET_COLUMN,
    new_model_version,
)


@dataclass
class ModelBundle:
    pipeline: Pipeline
    version: str
    features: list[str]
    path: Optional[Path] = None


class OutlierClipper(BaseEstimator, TransformerMixin):
    """
    Clip numeric features to configurable quantile bounds to reduce sensitivity
    to extreme values.
    """

    def __init__(self, lower_quantile: float = 0.01, upper_quantile: float = 0.99):
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile
        self.lower_bounds_: Optional[pd.Series] = None
        self.upper_bounds_: Optional[pd.Series] = None
        self.feature_names_in_: Optional[list] = None

    def fit(self, X, y=None):
        df = pd.DataFrame(X)
        self.lower_bounds_ = df.quantile(self.lower_quantile)
        self.upper_bounds_ = df.quantile(self.upper_quantile)
        self.feature_names_in_ = list(df.columns) if hasattr(df, 'columns') else None
        return self

    def transform(self, X):
        df = pd.DataFrame(X)
        clipped = df.clip(self.lower_bounds_, self.upper_bounds_, axis=1)
        return clipped.values
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names unchanged (clipping doesn't change feature names)."""
        if input_features is not None:
            return input_features
        if self.feature_names_in_ is not None:
            return self.feature_names_in_
        # Fallback: return generic names
        if hasattr(self, 'n_features_in_'):
            return [f"feature_{i}" for i in range(self.n_features_in_)]
        return []


def build_pipeline(random_state: int = RANDOM_STATE) -> Pipeline:
    """
    Assemble preprocessing + model pipeline.
    """
    numeric_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("clipper", OutlierClipper()),
        ]
    )

    categorical_pipeline = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        [
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
        ]
    )

    model = GradientBoostingRegressor(random_state=random_state)

    return Pipeline(
        [
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )


def evaluate_model(pipeline: Pipeline, X_val: pd.DataFrame, y_val: pd.Series) -> tuple[float, float]:
    preds = pipeline.predict(X_val)
    r2 = float(r2_score(y_val, preds))
    mae = float(mean_absolute_error(y_val, preds))
    return r2, mae


def train_model(data: pd.DataFrame, random_state: int = RANDOM_STATE) -> tuple[ModelBundle, float, float]:
    """
    Train pipeline and return the model bundle + metrics.
    """
    if data.empty:
        raise ValueError("Training data is empty")
    if TARGET_COLUMN not in data.columns:
        raise ValueError(f"Missing target column '{TARGET_COLUMN}'")

    X = data[FEATURE_COLUMNS]
    y = data[TARGET_COLUMN]

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )

    pipeline = build_pipeline(random_state=random_state)
    pipeline.fit(X_train, y_train)
    r2, mae = evaluate_model(pipeline, X_val, y_val)

    version = new_model_version()
    bundle = ModelBundle(pipeline=pipeline, version=version, features=FEATURE_COLUMNS)
    return bundle, r2, mae


def save_model(bundle: ModelBundle, models_dir: Path = MODELS_DIR) -> Path:
    models_dir.mkdir(parents=True, exist_ok=True)
    path = models_dir / f"{bundle.version}.joblib"
    joblib.dump(
        {
            "pipeline": bundle.pipeline,
            "version": bundle.version,
            "features": bundle.features,
        },
        path,
    )
    bundle.path = path
    return path


def load_latest_model(models_dir: Path = MODELS_DIR) -> Optional[ModelBundle]:
    if not models_dir.exists():
        return None

    candidates = sorted(models_dir.glob("model-*.joblib"))
    if not candidates:
        return None

    latest_path = candidates[-1]
    payload = joblib.load(latest_path)
    return ModelBundle(
        pipeline=payload["pipeline"],
        version=payload["version"],
        features=payload.get("features", FEATURE_COLUMNS),
        path=latest_path,
    )


def extract_feature_importances(pipeline: Pipeline) -> pd.DataFrame:
    """
    Extract feature importances from tree-based models, aligning them with
    transformed feature names.
    """
    model = pipeline.named_steps.get("model")
    preprocess = pipeline.named_steps.get("preprocess")

    if not hasattr(model, "feature_importances_") or preprocess is None:
        return pd.DataFrame(columns=["feature", "importance"])

    feature_names = list(preprocess.get_feature_names_out())
    importances = model.feature_importances_
    return (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )


def save_feature_importance(bundle: ModelBundle, output_dir: Path = OUTPUTS_DIR) -> pd.DataFrame:
    """
    Compute and persist feature importance CSV for the trained model.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    df_importance = extract_feature_importances(bundle.pipeline)
    path = output_dir / f"feature_importance_{bundle.version}.csv"
    df_importance.to_csv(path, index=False)
    return df_importance
