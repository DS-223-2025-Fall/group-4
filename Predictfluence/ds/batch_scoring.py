"""
Batch scoring utilities for Predictfluence.

Loads data from the DB or a CSV with the training schema, scores with the
latest saved model, segments predictions, and writes outputs to CSV for
downstream consumption (e.g., frontend recommendations).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
from sqlalchemy.orm import Session

from config import FEATURE_COLUMNS, OUTPUTS_DIR
from train import load_latest_model
from data import load_training_data_from_db

BATCH_OUTPUT_TEMPLATE = "batch_predictions_{version}.csv"


def load_batch_data(
    db: Optional[Session] = None, csv_path: Optional[str] = None
) -> pd.DataFrame:
    """
    Retrieve batch scoring data from a CSV (if provided) or the database join.
    """
    if csv_path:
        return pd.read_csv(csv_path)

    if db:
        return load_training_data_from_db(db)

    raise ValueError("Either db or csv_path must be provided to load batch data.")


def assign_segments(predictions: pd.Series) -> pd.Series:
    """
    Segment predictions: top 10% => A, next 30% => B, rest => C.
    """
    if predictions.empty:
        return pd.Series(dtype=str)

    q90 = predictions.quantile(0.9)
    q60 = predictions.quantile(0.6)

    def _segment(val: float) -> str:
        if val >= q90:
            return "A"
        if val >= q60:
            return "B"
        return "C"

    return predictions.apply(_segment)


def run_batch_scoring(
    db: Optional[Session] = None,
    csv_path: Optional[str] = None,
    outputs_dir: Path = OUTPUTS_DIR,
) -> Path:
    """
    Score a batch dataset and persist predictions + segments.
    """
    bundle = load_latest_model()
    if bundle is None:
        raise RuntimeError("No trained model artifact found for batch scoring.")

    data = load_batch_data(db=db, csv_path=csv_path)
    if data.empty:
        raise ValueError("No rows available for batch scoring.")

    missing_cols = [c for c in FEATURE_COLUMNS if c not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing required feature columns: {missing_cols}")

    preds = bundle.pipeline.predict(data[FEATURE_COLUMNS])
    pred_series = pd.Series(preds, name="predicted_engagement_rate")
    segments = assign_segments(pred_series)

    results = pd.DataFrame(
        {
            "content_id": data.get("content_id"),
            "influencer_id": data.get("influencer_id"),
            "predicted_engagement_rate": pred_series,
            "segment": segments,
            "model_version": bundle.version,
        }
    )

    outputs_dir.mkdir(parents=True, exist_ok=True)
    output_path = outputs_dir / BATCH_OUTPUT_TEMPLATE.format(version=bundle.version)
    results.to_csv(output_path, index=False)

    return output_path


def recommended_schema() -> dict:
    """
    Proposed JSON schema for a future /recommendations endpoint.
    """
    return {
        "type": "object",
        "properties": {
            "recommendations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "content_id": {"type": "integer"},
                        "influencer_id": {"type": "integer"},
                        "predicted_engagement_rate": {"type": "number"},
                        "segment": {"type": "string", "enum": ["A", "B", "C"]},
                        "model_version": {"type": "string"},
                        "explanation": {
                            "type": "array",
                            "description": "Optional feature importance snippets",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "feature": {"type": "string"},
                                    "contribution": {"type": "number"},
                                },
                                "required": ["feature", "contribution"],
                            },
                        },
                    },
                    "required": [
                        "content_id",
                        "influencer_id",
                        "predicted_engagement_rate",
                        "segment",
                        "model_version",
                    ],
                },
            }
        },
        "required": ["recommendations"],
    }
