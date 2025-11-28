"""
Centralized configuration for the Predictfluence DS service.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

# Feature definitions
NUMERIC_FEATURES: list[str] = ["follower_count", "tag_count", "caption_length"]
CATEGORICAL_FEATURES: list[str] = ["content_type", "category", "audience_top_country"]
FEATURE_COLUMNS: list[str] = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN: str = "engagement_rate"

# Training defaults
MIN_TRAINING_ROWS: int = 40
RANDOM_STATE: int = 42

# Artifact locations
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
OUTPUTS_DIR = BASE_DIR / "outputs"


def new_model_version(prefix: str = "model") -> str:
    """
    Generate a version string for model artifacts.
    """
    return datetime.utcnow().strftime(f"{prefix}-%Y%m%d%H%M%S")
