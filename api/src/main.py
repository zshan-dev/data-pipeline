from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session, joinedload
from typing import List

from . import models, schemas
from .database import Base, SessionLocal, engine, get_db
from .seed import seed_funded_status, seed_portfolio_targets
from .risk_engine import get_latest_funded_status, recalculate_funded_status

app = FastAPI()


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_portfolio_targets(db)
        seed_funded_status(db)
    finally:
        db.close()


@app.get("/")
def health():
    return {"status": "ok"}


@app.get("/news", response_model=List[schemas.MarketNews])
def get_news(limit: int = 50, sentiment_filter: str = "all", db: Session = Depends(get_db)):
    query = (
        db.query(models.MarketIntelligence)
        .options(joinedload(models.MarketIntelligence.asset))
        .order_by(models.MarketIntelligence.captured_at.desc())
    )

    if sentiment_filter == "positive":
        query = query.filter(models.MarketIntelligence.sentiment_score > 0)
    elif sentiment_filter == "negative":
        query = query.filter(models.MarketIntelligence.sentiment_score < 0)
    elif sentiment_filter == "neutral":
        query = query.filter(models.MarketIntelligence.sentiment_score == 0)

    rows = query.limit(limit).all()

    return [
        schemas.MarketNews(
            id=row.id,
            headline=row.headline,
            sentiment_score=row.sentiment_score,
            asset_class=row.asset.asset_class,
            captured_at=row.captured_at,
        )
        for row in rows
    ]


@app.get("/funded-status/latest", response_model=schemas.FundedStatusLatest)
def funded_status_latest(db: Session = Depends(get_db)):
    latest = get_latest_funded_status(db)
    if latest is None:
        # This should not happen because startup seeds a baseline row.
        # Raising keeps behavior explicit for demos.
        raise ValueError("No funded_status_log baseline found.")

    return schemas.FundedStatusLatest(
        id=latest.id,
        captured_at=latest.captured_at,
        total_assets=latest.total_assets,
        total_liabilities=latest.total_liabilities,
        funded_ratio=latest.funded_ratio,
    )


@app.post("/funded-status/recalculate", response_model=schemas.FundedStatusRecalculation)
def funded_status_recalculate(
    lookback_hours: int = 24,
    sensitivity: float = 0.02,
    db: Session = Depends(get_db),
):
    simulated = recalculate_funded_status(
        db=db,
        lookback_hours=lookback_hours,
        sensitivity=sensitivity,
        max_shock_pct=sensitivity,  # keep it tight for demo safety
    )

    return schemas.FundedStatusRecalculation(
        captured_at=simulated.captured_at,
        prior_total_assets=simulated.prior_total_assets,
        prior_total_liabilities=simulated.prior_total_liabilities,
        prior_funded_ratio=simulated.prior_funded_ratio,
        weighted_sentiment_score=simulated.weighted_sentiment_score,
        shock_pct=simulated.shock_pct,
        total_assets=simulated.total_assets,
        total_liabilities=simulated.total_liabilities,
        funded_ratio=simulated.funded_ratio,
    )
