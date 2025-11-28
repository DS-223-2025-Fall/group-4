# Predictfluence DS Service

End-to-end overview of the Data Science service that trains, serves, and batch-scores the engagement rate model.

## Purpose
Predict the `engagement_rate` of influencer content and expose the model over FastAPI for training (`/train`) and prediction (`/predict`), with support for batch scoring and explainability outputs.

## Data sources and joins
- **Tables**: `fact_content_features` and `fact_influencer_performance` (plus `content` for logging).
- **Join**: `fact_content_features.influencer_id = fact_influencer_performance.influencer_id`.
- **Loader**: `ds/data.py::load_training_data_from_db` selects the joined columns and returns a DataFrame; if empty, synthetic data is generated.

## Target and features
- **Target**: `engagement_rate`.
- **Core features** (fixed order):  
  1. `follower_count`  
  2. `tag_count`  
  3. `caption_length`  
  4. `content_type`  
  5. `category`  
  6. `audience_top_country`
- Feature lists are centralized in `ds/config.py`.

## Training workflow (`/train`)
- Entry point: `ds/main.py::train`.
- Data: Attempts DB join; if `< 40` rows, falls back to synthetic generation (`ds/data.py::simulate_training_data`).
- Model: GradientBoostingRegressor within a scikit-learn `Pipeline`:
  - Numeric: median impute + quantile outlier clipping.
  - Categorical: most-frequent impute + OneHotEncoder.
- Split: train/validation (80/20).
- Metrics: R² and MAE returned in the response.
- Outputs:
  - Model artifact saved to `ds/models/model-YYYYMMDDHHMMSS.joblib`.
  - Feature importance CSV saved to `ds/outputs/feature_importance_<model_version>.csv`.
  - Response fields: `n_rows`, `used_synthetic`, `r2`, `mae`, `model_version`, `features`, `top_features`.

## Prediction workflow (`/predict`)
- Entry point: `ds/main.py::predict` (proxied by `api/main.py`).
- Model loading: Always loads the latest artifact by version; trains on synthetic data if none exist.
- Required payload fields (fixed order): `follower_count`, `tag_count`, `caption_length`, `content_type`; optional `content_id`, `influencer_id`.
- Enrichment: If `influencer_id` is provided, `follower_count`, `category`, and `audience_top_country` are pulled from `fact_influencer_performance` when available; missing categoricals default to `"Unknown"`.
- Output: `predicted_engagement_rate`, `model_version`; logs to `prediction_logs` when `content_id` exists (stores `content_id`, `influencer_id`, prediction, model_version, timestamp) after FK validation.

## Artifacts, outputs, and versioning
- **Models**: `ds/models/model-YYYYMMDDHHMMSS.joblib` (version from UTC timestamp).
- **Feature importances**: `ds/outputs/feature_importance_<model_version>.csv`.
- Versioning: Generated via `config.new_model_version()`; latest artifact is loaded automatically for prediction/batch scoring.

## Batch scoring and segmentation
- Module: `ds/batch_scoring.py`.
- Data sources: DB join (`load_training_data_from_db`) or CSV with the same columns as training.
- Scoring: Uses the latest saved model; writes to `ds/outputs/batch_predictions_<model_version>.csv` with columns `content_id`, `influencer_id`, `predicted_engagement_rate`, `segment`, `model_version`.
- Segmentation: Based on predicted engagement rate — top 10% → `A`, next 30% → `B`, rest → `C`.
- Recommended JSON schema for future `/recommendations` endpoint is provided in `recommended_schema()` within `batch_scoring.py`.

## Service endpoints (DS)
- `GET /health`: readiness check.
- `POST /train`: triggers training, returns metrics, version, feature list, top features.
- `POST /predict`: scores a single payload, returns prediction and version, logs prediction when `content_id` is supplied.

## API proxy
- `api/main.py` exposes `/train` and `/predict` proxies to the DS service; configure DS URL via `DS_SERVICE_URL` (defaults to `http://localhost:8010`).
