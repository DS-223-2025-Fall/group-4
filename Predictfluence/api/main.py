from Database.models import InfluencerDB
from Database.schema import Influencer, InfluencerCreate
from Database.database import get_db, create_tables

from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException

app = FastAPI(title="Influencer Analytics Backend - Milestone 2")


@app.on_event("startup")
def startup_event():
    """
    Ensure all database tables exist when the API container starts.
    """
    create_tables()

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
