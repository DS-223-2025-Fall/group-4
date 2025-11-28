import os
from typing import Any, Dict

import requests
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from Database.database import get_db, create_tables
from Database.models import InfluencerDB
from Database.schema import Influencer, InfluencerCreate

DS_SERVICE_URL = os.getenv("DS_SERVICE_URL", "http://localhost:8010")

app = FastAPI(title="Influencer Analytics Backend - Milestone 2")


@app.on_event("startup")
def startup_event():
    """
    Ensure all database tables exist when the API container starts.
    """
    create_tables()


@app.post("/train")
def trigger_training() -> Dict[str, Any]:
    """
    Proxy to the DS service training endpoint and return its JSON payload.
    """
    url = f"{DS_SERVICE_URL.rstrip('/')}/train"
    try:
        resp = requests.post(url, timeout=120)
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail=f"DS service unavailable: {exc}") from exc

    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return resp.json()


class DSPredictPayload(BaseModel):
    """
    Pass-through schema for DS predict requests.
    """

    follower_count: int
    tag_count: int
    caption_length: int
    content_type: str
    content_id: int | None = None
    influencer_id: int | None = None


@app.post("/predict")
def proxy_predict(payload: DSPredictPayload) -> Dict[str, Any]:
    """
    Proxy predict requests to the DS service and return its JSON payload.
    """
    url = f"{DS_SERVICE_URL.rstrip('/')}/predict"
    try:
        resp = requests.post(url, json=payload.dict(), timeout=60)
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail=f"DS service unavailable: {exc}") from exc

    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return resp.json()

# -----------------------------
# GET Request - Retrieve influencer by ID
# -----------------------------
@app.get("/influencers/{influencer_id}", response_model=Influencer)
async def get_influencer(influencer_id: int, db: Session = Depends(get_db)):
    """
    Retrieve an influencer by their unique ID.

    Args:
        influencer_id (int): The unique identifier of the influencer.
        db (Session, optional): Database session provided by dependency injection.

    Returns:
        Influencer: The influencer's details.

    Raises:
        HTTPException: If the influencer is not found, raises a 404 error.
    """
    influencer = (
        db.query(InfluencerDB)
        .filter(InfluencerDB.influencer_id == influencer_id)
        .first()
    )
    if influencer is None:
        raise HTTPException(status_code=404, detail="Influencer not found")
    return influencer


# -----------------------------
# POST Request - Create a new influencer
# -----------------------------
@app.post("/influencers/", response_model=Influencer)
async def create_influencer(influencer: InfluencerCreate, db: Session = Depends(get_db)):
    """
    Create a new influencer.

    Args:
        influencer (InfluencerCreate): The influencer data required to create the record.
        db (Session, optional): Database session provided by dependency injection.

    Returns:
        Influencer: The newly created influencer's details.
    """
    db_influencer = InfluencerDB(
        name=influencer.name,
        username=influencer.username,
        platform=influencer.platform,
        follower_count=influencer.follower_count,
        category=influencer.category,
        created_at=influencer.created_at
    )

    db.add(db_influencer)
    db.commit()
    db.refresh(db_influencer)

    return Influencer(
        influencer_id=db_influencer.influencer_id,
        name=db_influencer.name,
        username=db_influencer.username,
        platform=db_influencer.platform,
        follower_count=db_influencer.follower_count,
        category=db_influencer.category,
        created_at=db_influencer.created_at
    )


# -----------------------------
# PUT Request - Update an existing influencer
# -----------------------------
@app.put("/influencers/{influencer_id}", response_model=Influencer)
async def update_influencer(
    influencer_id: int,
    updated_inf: InfluencerCreate,
    db: Session = Depends(get_db)
):
    """
    Update an existing influencer's details.

    Args:
        influencer_id (int): The unique identifier of the influencer.
        updated_inf (InfluencerCreate): The new influencer details.
        db (Session, optional): Database session provided by dependency injection.

    Returns:
        Influencer: The updated influencer details.

    Raises:
        HTTPException: If the influencer is not found, raises a 404 error.
    """
    influencer = (
        db.query(InfluencerDB)
        .filter(InfluencerDB.influencer_id == influencer_id)
        .first()
    )

    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")

    for key, value in updated_inf.dict().items():
        setattr(influencer, key, value)

    db.commit()
    db.refresh(influencer)

    return influencer


# -----------------------------
# DELETE Request - Delete influencer
# -----------------------------
@app.delete("/influencers/{influencer_id}")
async def delete_influencer(influencer_id: int, db: Session = Depends(get_db)):
    """
    Delete an influencer by their unique ID.

    Args:
        influencer_id (int): The unique identifier of the influencer.
        db (Session, optional): Database session provided by dependency injection.

    Returns:
        dict: A message confirming successful deletion.

    Raises:
        HTTPException: If the influencer is not found.
    """
    influencer = (
        db.query(InfluencerDB)
        .filter(InfluencerDB.influencer_id == influencer_id)
        .first()
    )

    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")

    db.delete(influencer)
    db.commit()

    return {"message": "Influencer deleted successfully"}
