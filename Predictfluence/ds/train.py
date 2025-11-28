"""
Lightweight facade that exposes the core training utilities for the DS service.

This module keeps the public API stable while the implementation details live in
focused modules (`config`, `data`, `modeling`).
"""

from __future__ import annotations

from config import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    MIN_TRAINING_ROWS,
    MODELS_DIR,
    NUMERIC_FEATURES,
    OUTPUTS_DIR,
    RANDOM_STATE,
    TARGET_COLUMN,
)
from data import load_training_data_from_db, simulate_training_data
from modeling import (
    ModelBundle,
    build_pipeline,
    evaluate_model,
    extract_feature_importances,
    load_latest_model,
    save_feature_importance,
    save_model,
    train_model,
)

__all__ = [
    "CATEGORICAL_FEATURES",
    "FEATURE_COLUMNS",
    "MIN_TRAINING_ROWS",
    "MODELS_DIR",
    "NUMERIC_FEATURES",
    "OUTPUTS_DIR",
    "RANDOM_STATE",
    "TARGET_COLUMN",
    "ModelBundle",
    "build_pipeline",
    "evaluate_model",
    "extract_feature_importances",
    "load_latest_model",
    "save_feature_importance",
    "save_model",
    "train_model",
    "load_training_data_from_db",
    "simulate_training_data",
]
