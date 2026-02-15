from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class PortfolioTarget(Base):
    __tablename__ = "portfolio_targets"
    
    id = Column(Integer, primary_key=True, index=True)
    asset_class = Column(String, unique=True, index=True, nullable=False)
    target_percentage = Column(Integer, nullable=False)
    risk_level = Column(String, nullable=True)

    news = relationship("MarketIntelligence", back_populates="asset")

class MarketIntelligence(Base):
    __tablename__ = "market_intelligence"

    id = Column(Integer, primary_key=True, index=True)
    captured_at = Column(DateTime)
    headline = Column(String, nullable=False)
    sentiment_score=Column(Float, default=0.0)
    asset_class_id = Column(Integer, ForeignKey("portfolio_targets.id"), nullable=False)

    asset = relationship("PortfolioTarget", back_populates="news")


class FundedStatusLog(Base):
    __tablename__ = "funded_status_log"

    id = Column(Integer, primary_key=True, index=True)
    captured_at = Column(DateTime, nullable=False, index=True)
    total_assets = Column(Float, nullable=False) 
    total_liabilities = Column(Float, nullable=False)
    funded_ratio = Column(Float, nullable=False)     