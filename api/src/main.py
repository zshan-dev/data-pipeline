from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session, joinedload
from typing import List

from . import models, schemas
from .database import Base, SessionLocal, engine, get_db
from .seed import seed_funded_status, seed_portfolio_targets

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
