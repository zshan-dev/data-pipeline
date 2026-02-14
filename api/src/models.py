from pydantic import BaseModel
from datetime import datetime

class MarketNews(BaseModel):
    id: int
    headline: str
    sentiment_score: float
    asset_class : str
    captured_at: datetime