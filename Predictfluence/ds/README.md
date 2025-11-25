# Predictfluence DS Service

Lightweight FastAPI service for data science tasks:
- trains a simple baseline engagement-rate model from the shared Postgres DB (falls back to synthetic data if the DB is empty)
- exposes `/train` and `/predict` endpoints
- logs predictions back to the `prediction_logs` table when a `content_id` is provided.

## Running locally (Docker)
1. Build/start via docker-compose (from repo root):
   ```bash
   docker-compose up -d --build ds
   ```
2. The service listens on `http://localhost:8010`. Handy routes:
   - `GET /health`
   - `POST /train`
   - `POST /predict`

## Environment
Configuration is read from `.env` inside this folder. By default it uses the
`postgresql_db` service defined in `docker-compose.yml`.

## Example predict payload
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

