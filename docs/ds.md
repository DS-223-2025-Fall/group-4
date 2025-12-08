# Data Science Service Documentation

The Data Science (DS) service provides machine learning models and analytics for engagement prediction, influencer classification, and insights.

## Access

- **URL**: http://localhost:8010
- **Port**: 8010 (configurable in `docker-compose.yml`)
- **Interactive Docs**: http://localhost:8010/docs

## Overview

The DS service provides:
1. **Engagement Rate Prediction**: Gradient Boosting Regressor
2. **Tier Classification**: Categorizes influencers as Elite/Professional/Emerging
3. **Influencer Clustering**: K-Means segmentation
4. **Skill Scores**: Performance-based influencer ranking
5. **Posting Schedule Optimization**: Time-aware analysis

## Endpoints

### Training

#### `POST /train`
Train the engagement rate prediction model.

**Response:**
```json
{
  "n_rows": 4378,
  "used_synthetic": false,
  "r2": 0.532,
  "mae": 0.011,
  "model_version": "model-20241208120538",
  "features": ["follower_count", "tag_count", "caption_length", "content_type", "category", "audience_top_country"]
}
```

**Auto-Training**: Model automatically trains on startup if database has ≥40 rows.

### Prediction

#### `POST /predict`
Predict engagement rate for content.

**Request Body:**
```json
{
  "follower_count": 120000,
  "tag_count": 3,
  "caption_length": 140,
  "content_type": "Video",
  "content_id": 10,
  "influencer_id": 2
}
```

**Response:**
```json
{
  "predicted_engagement_rate": 0.083,
  "model_version": "model-20241208120538",
  "logged": true
}
```

### Advanced Insights

#### `POST /insights/skill-scores`
Calculate influencer skill scores based on model residuals.

**Response:**
```json
{
  "scores": [
    {
      "influencer_id": 1,
      "n_posts": 25,
      "mean_residual": 0.012,
      "shrinkage_weight": 0.833,
      "skill_score": 0.010
    }
  ],
  "version": "skill-20241208120538"
}
```

#### `POST /insights/tier-classifier`
Train tier classification model.

**Response:**
```json
{
  "n_rows": 4378,
  "accuracy": 0.78,
  "f1_score": 0.75,
  "model_version": "tier-20241208120538"
}
```

#### `POST /insights/tier/predict`
Predict influencer tier for content.

**Request Body:**
```json
{
  "follower_count": 120000,
  "tag_count": 3,
  "caption_length": 140,
  "content_type": "Video"
}
```

**Response:**
```json
{
  "tier": "Elite",
  "confidence": 0.85,
  "model_version": "tier-20241208120538"
}
```

#### `POST /insights/clusters`
Cluster influencers using K-Means.

**Query Parameters:**
- `n_clusters` (default: 5): Number of clusters

**Response:**
```json
{
  "clusters": [
    {
      "cluster_id": 0,
      "influencer_ids": [1, 5, 12],
      "characteristics": {
        "avg_followers": 50000,
        "avg_engagement": 0.065
      }
    }
  ],
  "n_clusters": 5
}
```

#### `GET /insights/posting-schedule`
Get optimal posting schedule.

**Response:**
```json
{
  "best_days": ["Monday", "Wednesday", "Friday"],
  "best_hours": [14, 18, 20],
  "day_stats": {
    "Monday": 0.065,
    "Tuesday": 0.058
  },
  "hour_stats": {
    "14": 0.072,
    "18": 0.068
  }
}
```

#### `POST /batch-score`
Run batch scoring on all available data.

**Response:**
```json
{
  "n_scored": 150,
  "predictions": [
    {
      "influencer_id": 1,
      "content_id": 10,
      "predicted_engagement": 0.083,
      "tier": "Elite"
    }
  ]
}
```

## Model Details

### Engagement Rate Predictor

**Algorithm**: Gradient Boosting Regressor  
**Features**:
- Numeric: `follower_count`, `tag_count`, `caption_length`
- Categorical: `content_type`, `category`, `audience_top_country`

**Preprocessing**:
- Outlier clipping (1st-99th percentile)
- One-hot encoding for categorical features
- Missing value imputation

**Training**:
- 80/20 train/validation split
- Minimum 40 rows required
- Auto-trains on startup

**Metrics**:
- R² Score: Explained variance
- MAE: Mean Absolute Error

### Tier Classifier

**Algorithm**: Gradient Boosting Classifier  
**Classes**: Elite, Professional, Emerging  
**Features**: Same as engagement predictor  
**Output**: Tier label + confidence score

### Clustering

**Algorithm**: K-Means  
**Features**: Performance metrics (engagement, followers, etc.)  
**Output**: Cluster assignments + characteristics

### Posting Schedule

**Method**: Time-series analysis  
**Input**: Historical engagement by day/hour  
**Output**: Optimal posting times

## Model Persistence

Models are saved to:
- **Location**: `/ds/models/`
- **Format**: `.joblib` files
- **Naming**: `{model_type}-{timestamp}.joblib`

Example: `model-20241208120538.joblib`

## Feature Importance

Feature importance is saved to:
- **Location**: `/ds/outputs/`
- **Format**: CSV files
- **Naming**: `feature_importance_{model_version}.csv`

## Data Requirements

### Training Data
- Minimum: 40 rows
- Source: `fact_content_features` + `fact_influencer_performance` + `content`
- Fallback: Synthetic data if insufficient

### Features Required
- `follower_count`: Influencer follower count
- `tag_count`: Number of tags in caption
- `caption_length`: Length of caption
- `content_type`: Type of content (Image, Video, etc.)
- `category`: Influencer category
- `audience_top_country`: Top audience country

## Production Considerations

### Model Versioning
- Each training creates a new version
- Version includes timestamp
- Latest model is auto-loaded

### Performance
- Prediction latency: ~10-50ms
- Batch scoring: Optimized for bulk operations
- Caching: Models loaded in memory

### Monitoring
- Track prediction accuracy over time
- Monitor model drift
- Log prediction requests
- Alert on model degradation

---

For API integration, see [API Documentation](api.md)

