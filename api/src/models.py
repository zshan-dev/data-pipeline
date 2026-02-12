from pydantic import BaseModel

class MarketNews(BaseModel):
    id: int
    headline: str
    sentiment_score: float
    asset_class : str
    captured_at: datetime