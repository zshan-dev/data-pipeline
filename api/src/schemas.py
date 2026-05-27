from pydantic import BaseModel
from datetime import datetime

class MarketNews(BaseModel):
    id: int
    headline: str
    sentiment_score: float
    asset_class : str
    captured_at: datetime


class FundedStatusLatest(BaseModel):
    id: int
    captured_at: datetime
    total_assets: float
    total_liabilities: float
    funded_ratio: float


class FundedStatusRecalculation(BaseModel):
    captured_at: datetime

    # Inputs / baseline
    prior_total_assets: float
    prior_total_liabilities: float
    prior_funded_ratio: float

    # Model internals (so it’s explainable in a demo)
    weighted_sentiment_score: float
    shock_pct: float

    # Outputs
    total_assets: float
    total_liabilities: float
    funded_ratio: float