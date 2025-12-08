"""
Predictfluence API (Milestone 3)

Implements the endpoints specified in docs/api.md. Auth is a lightweight
demo flow until the dedicated users table is delivered by the DB developer.
"""

import os
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import requests
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session
from pydantic import BaseModel

from Database.database import create_tables, get_db
from Database.models import (
    Base,
    APILogDB,
    AudienceDemographicsDB,
    BrandDB,
    CampaignContentDB,
    CampaignDB,
    ContentDB,
    EngagementDB,
    FactContentFeaturesDB,
    FactInfluencerPerformanceDB,
    InfluencerDB,
    PredictionLogDB,
    UserDB,
)
from Database.schema import (
    AudienceDemographics,
    Brand,
    BrandCreate,
    Campaign,
    CampaignContentCreate,
    CampaignCreate,
    Content,
    ContentCreate,
    Engagement,
    EngagementCreate,
    Influencer,
    InfluencerCreate,
)
from schemas import (
    APILogListResponse,
    AudienceAnalyticsResponse,
    BatchScoringResponse,
    CampaignDetail,
    CampaignInfluencerPerformanceRow,
    CampaignListResponse,
    CampaignSummary,
    ClusterResponse,
    ContentDetail,
    CountResponse,
    CreativeAnalyticsResponse,
    EngagementSeriesResponse,
    HealthResponse,
    InfluencerDetail,
    InfluencerListResponse,
    LoginRequest,
    MLPredictRequest,
    MLPredictResponse,
    MLTrainResponse,
    PerformanceAnalyticsResponse,
    RecommendationRequest,
    RecommendationResponse,
    ScheduleResponse,
    SkillScoresResponse,
    TierPredictRequest,
    TierPredictResponse,
    TierTrainResponse,
    TokenResponse,
    TopCampaignsResponse,
    UserProfile,
    UserUpdate,
)


API_TITLE = "Influencer Analytics Backend - Milestone 3"
DS_URL = os.getenv("DS_URL", "http://ds:8010")

app = FastAPI(title=API_TITLE)


@app.on_event("startup")
def startup_event() -> None:
    """Ensure all database tables exist when the API container starts."""
    create_tables()


@app.post("/train")
def trigger_training() -> Dict[str, Any]:
    """
    Proxy to the DS service training endpoint and return its JSON payload.
    """
    url = f"{DS_URL.rstrip('/')}/train"
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
    url = f"{DS_URL.rstrip('/')}/predict"
    try:
        resp = requests.post(url, json=payload.dict(), timeout=60)
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail=f"DS service unavailable: {exc}") from exc

    if not resp.ok:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return resp.json()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def log_api_call(db: Session, user: str, endpoint: str, status: str) -> None:
    """Persist a simple API log entry."""
    try:
        db.add(APILogDB(user=user, endpoint=endpoint, status=status))
        db.commit()
    except Exception:
        db.rollback()


def paginate(query, page: int, page_size: int):
    offset = (page - 1) * page_size
    return query.offset(offset).limit(page_size)


def get_date_cutoff(range_str: str) -> Optional[date]:
    if not range_str or not range_str.endswith("d"):
        return None
    try:
        days = int(range_str[:-1])
        return date.today() - timedelta(days=days)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Auth / User
# ---------------------------------------------------------------------------
@app.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Demo login: look up or create a user row and return a bearer token stub."""
    user = db.query(UserDB).filter(UserDB.email == payload.email).first()

    if user and user.hashed_password != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user:
        user = UserDB(
            email=payload.email,
            hashed_password=payload.password,
            full_name=payload.full_name,
            role=payload.role or "User",
            company=payload.company,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = f"demo-token-{user.email}"
    return TokenResponse(
        access_token=token,
        user=UserProfile(
            email=user.email,
            role=user.role,
            company=user.company,
            full_name=user.full_name,
        ),
    )


@app.get("/user/profile", response_model=UserProfile)
def get_profile(email: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Return the current user profile; falls back to the first user for demo mode."""
    query = db.query(UserDB)
    user = query.filter(UserDB.email == email).first() if email else query.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile(
        email=user.email,
        role=user.role,
        company=user.company,
        full_name=user.full_name,
    )


@app.put("/user/profile", response_model=UserProfile)
def update_profile(update: UserUpdate, email: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Update basic user fields; selects by email or the first user row."""
    query = db.query(UserDB)
    user = query.filter(UserDB.email == email).first() if email else query.first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for field, value in update.dict(exclude_unset=True).items():
        if value is not None:
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return UserProfile(
        email=user.email,
        role=user.role,
        company=user.company,
        full_name=user.full_name,
    )


# ---------------------------------------------------------------------------
# Influencers
# ---------------------------------------------------------------------------
@app.get("/influencers", response_model=InfluencerListResponse)
def list_influencers(
    platform: Optional[str] = None,
    category: Optional[str] = None,
    min_followers: Optional[int] = Query(None, ge=0),
    max_followers: Optional[int] = Query(None, ge=0),
    country: Optional[str] = None,
    q: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List influencers with filters and pagination."""
    query = db.query(InfluencerDB)

    if platform:
        query = query.filter(InfluencerDB.platform == platform)
    if category:
        query = query.filter(InfluencerDB.category == category)
    if min_followers is not None:
        query = query.filter(InfluencerDB.follower_count >= min_followers)
    if max_followers is not None:
        query = query.filter(InfluencerDB.follower_count <= max_followers)
    if q:
        ilike = f"%{q}%"
        query = query.filter(or_(InfluencerDB.name.ilike(ilike), InfluencerDB.username.ilike(ilike)))
    if country:
        query = query.join(FactInfluencerPerformanceDB, FactInfluencerPerformanceDB.influencer_id == InfluencerDB.influencer_id)
        query = query.filter(FactInfluencerPerformanceDB.audience_top_country == country)

    total = query.count()
    records = paginate(query.order_by(InfluencerDB.influencer_id.asc()), page, page_size).all()
    return InfluencerListResponse(items=records, total=total)


@app.get("/influencers/{influencer_id}", response_model=InfluencerDetail)
def get_influencer(influencer_id: int, include: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Retrieve an influencer with optional performance and audience sections."""
    influencer = db.query(InfluencerDB).filter(InfluencerDB.influencer_id == influencer_id).first()
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")

    include_flags = set((include or "").split(",")) if include else set()
    performance = None
    audience = None

    if "performance" in include_flags:
        performance = (
            db.query(FactInfluencerPerformanceDB)
            .filter(FactInfluencerPerformanceDB.influencer_id == influencer_id)
            .first()
        )

    if "audience" in include_flags:
        audience = (
            db.query(AudienceDemographicsDB)
            .filter(AudienceDemographicsDB.influencer_id == influencer_id)
            .all()
        )

    return InfluencerDetail(influencer=influencer, performance=performance, audience=audience)


@app.post("/influencers", response_model=Influencer)
def create_influencer(influencer: InfluencerCreate, db: Session = Depends(get_db)):
    """Create a new influencer record."""
    db_influencer = InfluencerDB(**influencer.dict())
    db.add(db_influencer)
    db.commit()
    db.refresh(db_influencer)
    return db_influencer


@app.put("/influencers/{influencer_id}", response_model=Influencer)
def update_influencer(influencer_id: int, updated_inf: InfluencerCreate, db: Session = Depends(get_db)):
    """Update an influencer by ID."""
    influencer = db.query(InfluencerDB).filter(InfluencerDB.influencer_id == influencer_id).first()
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")

    for key, value in updated_inf.dict().items():
        setattr(influencer, key, value)

    db.commit()
    db.refresh(influencer)
    return influencer


@app.delete("/influencers/{influencer_id}")
def delete_influencer(influencer_id: int, db: Session = Depends(get_db)):
    """Delete an influencer by ID."""
    influencer = db.query(InfluencerDB).filter(InfluencerDB.influencer_id == influencer_id).first()
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")

    db.delete(influencer)
    db.commit()
    return {"message": "deleted"}


@app.get("/influencers/{influencer_id}/audience", response_model=List[AudienceDemographics])
def list_audience(influencer_id: int, db: Session = Depends(get_db)):
    """Return audience demographics for an influencer."""
    records = (
        db.query(AudienceDemographicsDB)
        .filter(AudienceDemographicsDB.influencer_id == influencer_id)
        .all()
    )
    return records


@app.get("/influencers/{influencer_id}/content", response_model=List[Content])
def list_influencer_content(
    influencer_id: int,
    content_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    """List content for an influencer with optional filters."""
    query = db.query(ContentDB).filter(ContentDB.influencer_id == influencer_id)
    if content_type:
        query = query.filter(ContentDB.content_type == content_type)
    if start_date:
        query = query.filter(ContentDB.post_date >= start_date)
    if end_date:
        query = query.filter(ContentDB.post_date <= end_date)
    return query.order_by(ContentDB.post_date.desc().nullslast()).all()


@app.get("/influencers/count", response_model=CountResponse)
def count_influencers(db: Session = Depends(get_db)):
    """Return the total influencer count (for dashboard KPI)."""
    count = db.query(func.count(InfluencerDB.influencer_id)).scalar() or 0
    return CountResponse(count=count)


# ---------------------------------------------------------------------------
# Content & Engagement
# ---------------------------------------------------------------------------
@app.post("/content", response_model=Content)
def create_content(payload: ContentCreate, db: Session = Depends(get_db)):
    """Create a content row."""
    influencer = db.query(InfluencerDB).filter(InfluencerDB.influencer_id == payload.influencer_id).first()
    if not influencer:
        raise HTTPException(status_code=404, detail="Influencer not found")

    content = ContentDB(**payload.dict())
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


@app.get("/content/{content_id}", response_model=ContentDetail)
def get_content(content_id: int, db: Session = Depends(get_db)):
    """Return content plus engagement and campaign link IDs."""
    content = db.query(ContentDB).filter(ContentDB.content_id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    engagement = db.query(EngagementDB).filter(EngagementDB.content_id == content_id).first()
    links = db.query(CampaignContentDB).filter(CampaignContentDB.content_id == content_id).all()
    link_ids = [link.campaign_id for link in links]
    return ContentDetail(content=content, engagement=engagement, campaigns=link_ids)


@app.post("/content/{content_id}/engagement", response_model=Engagement)
def upsert_engagement(content_id: int, payload: EngagementCreate, db: Session = Depends(get_db)):
    """Create or update engagement for a content item."""
    content = db.query(ContentDB).filter(ContentDB.content_id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    engagement = db.query(EngagementDB).filter(EngagementDB.content_id == content_id).first()
    if engagement:
        for key, value in payload.dict().items():
            setattr(engagement, key, value)
    else:
        engagement = EngagementDB(**payload.dict())
        db.add(engagement)

    db.commit()
    db.refresh(engagement)
    return engagement


@app.get("/content/{content_id}/engagement", response_model=Engagement)
def get_engagement(content_id: int, db: Session = Depends(get_db)):
    """Retrieve engagement for a content item."""
    engagement = db.query(EngagementDB).filter(EngagementDB.content_id == content_id).first()
    if not engagement:
        raise HTTPException(status_code=404, detail="Engagement not found")
    return engagement


# ---------------------------------------------------------------------------
# Brands & Campaigns
# ---------------------------------------------------------------------------
@app.get("/brands", response_model=List[Brand])
def list_brands(db: Session = Depends(get_db)):
    """List all brands."""
    return db.query(BrandDB).order_by(BrandDB.brand_id.asc()).all()


@app.post("/brands", response_model=Brand)
def create_brand(payload: BrandCreate, db: Session = Depends(get_db)):
    """Create a brand."""
    brand = BrandDB(**payload.dict())
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


@app.get("/brands/{brand_id}", response_model=Brand)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    """Retrieve a brand by ID."""
    brand = db.query(BrandDB).filter(BrandDB.brand_id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@app.get("/campaigns", response_model=CampaignListResponse)
def list_campaigns(
    brand_id: Optional[int] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List campaigns with filters and pagination."""
    query = db.query(CampaignDB)
    if brand_id:
        query = query.filter(CampaignDB.brand_id == brand_id)
    if status:
        query = query.filter(CampaignDB.status == status)
    if start_date:
        query = query.filter(CampaignDB.start_date >= start_date)
    if end_date:
        query = query.filter(CampaignDB.end_date <= end_date)

    total = query.count()
    records = paginate(query.order_by(CampaignDB.campaign_id.asc()), page, page_size).all()
    return CampaignListResponse(items=records, total=total)


@app.post("/campaigns", response_model=Campaign)
def create_campaign(payload: CampaignCreate, db: Session = Depends(get_db)):
    """Create a new campaign."""
    brand = db.query(BrandDB).filter(BrandDB.brand_id == payload.brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    campaign = CampaignDB(**payload.dict())
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


@app.get("/campaigns/{campaign_id}", response_model=CampaignDetail)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Return a campaign with brand info and linked content IDs."""
    campaign = db.query(CampaignDB).filter(CampaignDB.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    brand = db.query(BrandDB).filter(BrandDB.brand_id == campaign.brand_id).first()
    links = db.query(CampaignContentDB).filter(CampaignContentDB.campaign_id == campaign_id).all()
    return CampaignDetail(campaign=campaign, brand=brand, content_links=links)


@app.put("/campaigns/{campaign_id}", response_model=Campaign)
def update_campaign(campaign_id: int, payload: CampaignCreate, db: Session = Depends(get_db)):
    """Update a campaign."""
    campaign = db.query(CampaignDB).filter(CampaignDB.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    for key, value in payload.dict().items():
        setattr(campaign, key, value)

    db.commit()
    db.refresh(campaign)
    return campaign


@app.delete("/campaigns/{campaign_id}")
def delete_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Delete a campaign."""
    campaign = db.query(CampaignDB).filter(CampaignDB.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    db.delete(campaign)
    db.commit()
    return {"message": "deleted"}


@app.get("/campaigns/{campaign_id}/summary", response_model=CampaignSummary)
def campaign_summary(campaign_id: int, db: Session = Depends(get_db)):
    """Summarize campaign metrics using linked content and engagement."""
    campaign = db.query(CampaignDB).filter(CampaignDB.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    engagement_rows = (
        db.query(EngagementDB)
        .join(ContentDB, ContentDB.content_id == EngagementDB.content_id)
        .join(CampaignContentDB, CampaignContentDB.content_id == ContentDB.content_id)
        .filter(CampaignContentDB.campaign_id == campaign_id)
        .all()
    )

    influencer_ids = (
        db.query(ContentDB.influencer_id)
        .join(CampaignContentDB, CampaignContentDB.content_id == ContentDB.content_id)
        .filter(CampaignContentDB.campaign_id == campaign_id)
        .distinct()
        .all()
    )
    influencer_count = len(influencer_ids)

    avg_eng_rate = 0.0
    avg_views = 0.0
    if engagement_rows:
        avg_eng_rate = float(
            sum(row.engagement_rate or 0.0 for row in engagement_rows) / len(engagement_rows)
        )
        avg_views = float(sum(row.views or 0 for row in engagement_rows) / len(engagement_rows))

    # spend_to_date and avg_cost_per_influencer require finance fields; keep placeholders.
    spend_to_date = 0.0
    avg_cost_per_influencer = 0.0

    return CampaignSummary(
        campaign_id=campaign.campaign_id,
        name=campaign.name,
        budget=campaign.budget,
        status=campaign.status,
        spend_to_date=spend_to_date,
        influencer_count=influencer_count,
        avg_engagement_rate=avg_eng_rate,
        avg_views=avg_views,
        avg_cost_per_influencer=avg_cost_per_influencer,
    )


@app.get("/campaigns/{campaign_id}/influencer-performance", response_model=List[CampaignInfluencerPerformanceRow])
def campaign_influencer_performance(campaign_id: int, db: Session = Depends(get_db)):
    """Return influencer/content performance rows for a campaign."""
    rows = (
        db.query(
            ContentDB.influencer_id,
            ContentDB.content_id,
            InfluencerDB.platform,
            EngagementDB.engagement_rate,
            EngagementDB.likes,
            EngagementDB.comments,
            EngagementDB.views,
            CampaignContentDB.role,
            CampaignContentDB.is_paid,
        )
        .join(ContentDB, ContentDB.content_id == CampaignContentDB.content_id)
        .join(InfluencerDB, InfluencerDB.influencer_id == ContentDB.influencer_id)
        .outerjoin(EngagementDB, EngagementDB.content_id == ContentDB.content_id)
        .filter(CampaignContentDB.campaign_id == campaign_id)
        .all()
    )

    return [
        CampaignInfluencerPerformanceRow(
            influencer_id=r[0],
            content_id=r[1],
            platform=r[2],
            engagement_rate=r[3],
            likes=r[4],
            comments=r[5],
            views=r[6],
            role=r[7],
            is_paid=r[8],
        )
        for r in rows
    ]


@app.post("/campaigns/{campaign_id}/content")
def attach_content(campaign_id: int, payload: CampaignContentCreate, db: Session = Depends(get_db)):
    """Link content to a campaign."""
    campaign = db.query(CampaignDB).filter(CampaignDB.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    content = db.query(ContentDB).filter(ContentDB.content_id == payload.content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    existing = (
        db.query(CampaignContentDB)
        .filter(
            CampaignContentDB.campaign_id == campaign_id,
            CampaignContentDB.content_id == payload.content_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Content already linked to campaign")

    link = CampaignContentDB(
        campaign_id=campaign_id,
        content_id=payload.content_id,
        role=payload.role,
        is_paid=payload.is_paid,
    )
    db.add(link)
    db.commit()
    return {"message": "linked"}


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------
@app.get("/analytics/engagement", response_model=EngagementSeriesResponse)
def analytics_engagement(range: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Engagement over time (grouped by content post_date)."""
    cutoff = get_date_cutoff(range)

    query = (
        db.query(ContentDB.post_date, func.avg(EngagementDB.engagement_rate))
        .join(EngagementDB, EngagementDB.content_id == ContentDB.content_id)
        .group_by(ContentDB.post_date)
        .order_by(ContentDB.post_date)
    )
    if cutoff:
        query = query.filter(ContentDB.post_date >= cutoff)

    series = [
        {"date": row[0], "engagement_rate": float(row[1] or 0.0)}
        for row in query.all()
        if row[0]
    ]
    return EngagementSeriesResponse(series=series)


@app.get("/analytics/top-campaigns", response_model=TopCampaignsResponse)
def analytics_top_campaigns(limit: int = Query(5, ge=1, le=50), metric: str = Query("engagement"), db: Session = Depends(get_db)):
    """Top campaigns ranked by average engagement rate."""
    metric_column = EngagementDB.engagement_rate if metric == "engagement" else EngagementDB.views

    rows = (
        db.query(
            CampaignDB.campaign_id,
            CampaignDB.name,
            func.avg(metric_column).label("metric"),
        )
        .join(CampaignContentDB, CampaignContentDB.campaign_id == CampaignDB.campaign_id)
        .join(ContentDB, ContentDB.content_id == CampaignContentDB.content_id)
        .join(EngagementDB, EngagementDB.content_id == ContentDB.content_id)
        .group_by(CampaignDB.campaign_id, CampaignDB.name)
        .order_by(func.avg(metric_column).desc())
        .limit(limit)
        .all()
    )

    items = [
        {
            "campaign_id": row[0],
            "name": row[1],
            "metric_value": float(row[2] or 0.0),
            "rank": idx + 1,
        }
        for idx, row in enumerate(rows)
    ]
    return TopCampaignsResponse(items=items)


@app.get("/analytics/audience", response_model=AudienceAnalyticsResponse)
def analytics_audience(group_by: str = Query("country"), db: Session = Depends(get_db)):
    """Aggregate audience demographics by the requested dimension."""
    valid_groups = {"country", "age_group", "gender"}
    if group_by not in valid_groups:
        raise HTTPException(status_code=400, detail="Invalid group_by")

    field = getattr(AudienceDemographicsDB, group_by)
    rows = (
        db.query(field, func.sum(AudienceDemographicsDB.percentage))
        .group_by(field)
        .order_by(func.sum(AudienceDemographicsDB.percentage).desc())
        .all()
    )
    items = [
        {"group": row[0], "percentage": float(row[1] or 0.0)}
        for row in rows
    ]
    return AudienceAnalyticsResponse(group_by=group_by, items=items)


@app.get("/analytics/creative", response_model=CreativeAnalyticsResponse)
def analytics_creative(db: Session = Depends(get_db)):
    """Engagement by content type/topic."""
    rows = (
        db.query(ContentDB.content_type, ContentDB.topic, func.avg(EngagementDB.engagement_rate))
        .outerjoin(EngagementDB, EngagementDB.content_id == ContentDB.content_id)
        .group_by(ContentDB.content_type, ContentDB.topic)
        .all()
    )
    items = [
        {
            "content_type": row[0],
            "topic": row[1],
            "avg_engagement_rate": float(row[2] or 0.0),
        }
        for row in rows
    ]
    return CreativeAnalyticsResponse(items=items)


@app.get("/analytics/performance", response_model=PerformanceAnalyticsResponse)
def analytics_performance(db: Session = Depends(get_db)):
    """Overall KPI rollup from engagement table."""
    agg = (
        db.query(
            func.avg(EngagementDB.engagement_rate),
            func.avg(EngagementDB.likes),
            func.avg(EngagementDB.comments),
            func.avg(EngagementDB.views),
        )
        .first()
    )
    return PerformanceAnalyticsResponse(
        avg_engagement_rate=float(agg[0] or 0.0),
        avg_likes=float(agg[1] or 0.0),
        avg_comments=float(agg[2] or 0.0),
        avg_views=float(agg[3] or 0.0),
    )


# ---------------------------------------------------------------------------
# Recommendations / ML
# ---------------------------------------------------------------------------
@app.post("/recommendations", response_model=RecommendationResponse)
def recommendations(payload: RecommendationRequest, db: Session = Depends(get_db)):
    """
    ML-powered recommendations using batch scoring and tier classification.
    Filters influencers by criteria and returns top performers with predictions.
    """
    # Step 1: Filter influencers by criteria
    query = db.query(InfluencerDB)
    if payload.platform:
        query = query.filter(InfluencerDB.platform == payload.platform)
    if payload.category:
        query = query.filter(InfluencerDB.category == payload.category)
    
    influencers = query.limit(50).all()  # Get more candidates for ML scoring
    
    if not influencers:
        return RecommendationResponse(recommendations=[])
    
    # Step 2: Get performance data for these influencers
    influencer_ids = [inf.influencer_id for inf in influencers]
    perf_data = (
        db.query(FactInfluencerPerformanceDB)
        .filter(FactInfluencerPerformanceDB.influencer_id.in_(influencer_ids))
        .all()
    )
    perf_dict = {p.influencer_id: p for p in perf_data}
    
    # Step 3: Get content features for these influencers to make predictions
    content_features = (
        db.query(FactContentFeaturesDB)
        .filter(FactContentFeaturesDB.influencer_id.in_(influencer_ids))
        .limit(100)
        .all()
    )
    
    if not content_features:
        # Fallback: use basic heuristics if no content data
        recs = []
        for inf in influencers[:10]:
            perf = perf_dict.get(inf.influencer_id)
            predicted = 0.05  # Default low prediction
            if perf:
                predicted = max(0.01, min(0.25, (perf.follower_count or 1) ** -0.3))
            
            recs.append({
                "influencer_id": inf.influencer_id,
                "influencer_name": inf.name,
                "platform": inf.platform,
                "predicted_engagement": float(predicted),
                "rationale": "Limited data available; using performance heuristics",
                "content_id": None,
            })
        return RecommendationResponse(recommendations=recs)
    
    # Step 4: Use ML service to predict engagement for content pieces
    recs = []
    predictions_made = {}
    
    for cf in content_features[:20]:  # Limit to avoid too many API calls
        inf = next((i for i in influencers if i.influencer_id == cf.influencer_id), None)
        if not inf:
            continue
        
        perf = perf_dict.get(cf.influencer_id)
        if not perf:
            continue
        
        # Build prediction request
        try:
            pred_payload = {
                "follower_count": perf.follower_count or 1000,
                "tag_count": cf.tag_count or 0,
                "caption_length": cf.caption_length or 0,
                "content_type": cf.content_type or "Image",
                "influencer_id": cf.influencer_id,
                "content_id": cf.content_id,
            }
            
            resp = requests.post(f"{DS_URL}/predict", json=pred_payload, timeout=5)
            if resp.ok:
                pred_data = resp.json()
                predicted = pred_data.get("predicted_engagement_rate", 0.0)
                predictions_made[cf.influencer_id] = max(
                    predictions_made.get(cf.influencer_id, 0.0),
                    predicted
                )
        except Exception:
            continue  # Skip if prediction fails
    
    # Step 5: Build recommendations sorted by predicted engagement
    for inf in influencers:
        if inf.influencer_id in predictions_made:
            perf = perf_dict.get(inf.influencer_id)
            rationale_parts = []
            if payload.platform:
                rationale_parts.append(f"Platform: {payload.platform}")
            if payload.category:
                rationale_parts.append(f"Category: {payload.category}")
            rationale_parts.append("ML-predicted engagement rate")
            
            recs.append({
                "influencer_id": inf.influencer_id,
                "influencer_name": inf.name,
                "platform": inf.platform,
                "predicted_engagement": float(predictions_made[inf.influencer_id]),
                "rationale": "; ".join(rationale_parts),
                "content_id": None,
            })
    
    # Sort by predicted engagement (descending) and limit to top 10
    recs.sort(key=lambda x: x["predicted_engagement"], reverse=True)
    
    # If we have fewer than 10 ML predictions, fill with filtered influencers
    if len(recs) < 10:
        for inf in influencers:
            if inf.influencer_id not in predictions_made:
                perf = perf_dict.get(inf.influencer_id)
                predicted = 0.03  # Lower default for non-ML
                if perf:
                    predicted = max(0.01, min(0.20, (perf.follower_count or 1) ** -0.3))
                
                recs.append({
                    "influencer_id": inf.influencer_id,
                    "influencer_name": inf.name,
                    "platform": inf.platform,
                    "predicted_engagement": float(predicted),
                    "rationale": "Filtered match; estimated engagement",
                    "content_id": None,
                })
                if len(recs) >= 10:
                    break
    
    return RecommendationResponse(recommendations=recs[:10])


@app.post("/ml/train", response_model=MLTrainResponse)
def ml_train(db: Session = Depends(get_db)):
    """Proxy to the DS service /train endpoint."""
    try:
        resp = requests.post(f"{DS_URL}/train", timeout=20)
        resp.raise_for_status()
        return MLTrainResponse(**resp.json())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"ML train failed: {exc}")


@app.post("/ml/predict", response_model=MLPredictResponse)
def ml_predict(payload: MLPredictRequest, db: Session = Depends(get_db)):
    """Proxy to the DS service /predict endpoint."""
    try:
        resp = requests.post(f"{DS_URL}/predict", json=payload.dict(), timeout=10)
        resp.raise_for_status()
        return MLPredictResponse(**resp.json())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"ML predict failed: {exc}")


# ---------------------------------------------------------------------------
# Advanced ML / Insights Endpoints
# ---------------------------------------------------------------------------
@app.post("/ml/insights/skill-scores", response_model=SkillScoresResponse)
def ml_skill_scores(db: Session = Depends(get_db)):
    """Get influencer skill scores based on model residuals."""
    try:
        resp = requests.post(f"{DS_URL}/insights/skill-scores", timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return SkillScoresResponse(**data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Skill scores failed: {exc}")


@app.post("/ml/insights/tier/predict", response_model=TierPredictResponse)
def ml_tier_predict(payload: TierPredictRequest, db: Session = Depends(get_db)):
    """Predict content tier (A/B/C) for a single content piece."""
    try:
        resp = requests.post(f"{DS_URL}/insights/tier/predict", json=payload.dict(), timeout=10)
        resp.raise_for_status()
        return TierPredictResponse(**resp.json())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Tier prediction failed: {exc}")


@app.post("/ml/insights/tier/train", response_model=TierTrainResponse)
def ml_tier_train(db: Session = Depends(get_db)):
    """Train the tier classifier model."""
    try:
        resp = requests.post(f"{DS_URL}/insights/tier/train", timeout=30)
        resp.raise_for_status()
        return TierTrainResponse(**resp.json())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Tier training failed: {exc}")


@app.post("/ml/insights/clusters", response_model=ClusterResponse)
def ml_clusters(n_clusters: int = Query(5, ge=2, le=10), db: Session = Depends(get_db)):
    """Cluster influencers using KMeans for segmentation."""
    try:
        resp = requests.post(f"{DS_URL}/insights/clusters", params={"n_clusters": n_clusters}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return ClusterResponse(**data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Clustering failed: {exc}")


@app.get("/ml/insights/posting-schedule", response_model=ScheduleResponse)
def ml_posting_schedule(db: Session = Depends(get_db)):
    """Get optimal posting schedule based on historical engagement patterns."""
    try:
        resp = requests.get(f"{DS_URL}/insights/posting-schedule", timeout=20)
        resp.raise_for_status()
        data = resp.json()
        return ScheduleResponse(**data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Schedule analysis failed: {exc}")


@app.post("/ml/batch-score", response_model=BatchScoringResponse)
def ml_batch_score(db: Session = Depends(get_db)):
    """Run batch scoring on all available data and return predictions with segments."""
    try:
        resp = requests.post(f"{DS_URL}/batch-score", timeout=60)
        resp.raise_for_status()
        return BatchScoringResponse(**resp.json())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Batch scoring failed: {exc}")


# ---------------------------------------------------------------------------
# Health / Logs
# ---------------------------------------------------------------------------
@app.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)):
    """Return DB connectivity status."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"
    return HealthResponse(status="ok", db=db_status)


@app.get("/logs/api", response_model=APILogListResponse)
def api_logs(limit: int = Query(50, ge=1, le=500), db: Session = Depends(get_db)):
    """Return recent API logs (demo; no auth checks)."""
    rows = db.query(APILogDB).order_by(APILogDB.timestamp.desc()).limit(limit).all()
    return APILogListResponse(items=rows)
