from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional


@dataclass(frozen=True)
class SimulatedFundedStatus:
    captured_at: datetime
    prior_total_assets: float
    prior_total_liabilities: float
    prior_funded_ratio: float
    weighted_sentiment_score: float
    shock_pct: float
    total_assets: float
    total_liabilities: float
    funded_ratio: float


def compute_weighted_sentiment_score(
    sentiment_by_asset_class: Dict[str, float],
    weights_by_asset_class: Dict[str, float],
) -> float:
    """
    Weighted average sentiment across asset classes.

    Missing sentiment for an asset is treated as 0.0.
    """
    total_weight = sum(weights_by_asset_class.values())
    if total_weight == 0:
        return 0.0

    weighted_sum = 0.0
    for asset_class, weight in weights_by_asset_class.items():
        weighted_sum += sentiment_by_asset_class.get(asset_class, 0.0) * weight

    return weighted_sum / total_weight


def simulate_funded_status(
    prior_total_assets: float,
    prior_total_liabilities: float,
    weighted_sentiment_score: float,
    *,
    sensitivity: float = 0.02,
    max_shock_pct: float = 0.02,
    captured_at: Optional[datetime] = None,
) -> SimulatedFundedStatus:
    """
    v1 simulation:
    - Convert portfolio sentiment into a small % "asset shock"
    - Liabilities unchanged
    - Recompute funded ratio and log the new scenario
    """
    if captured_at is None:
        captured_at = datetime.utcnow()

    if prior_total_liabilities <= 0:
        raise ValueError("prior_total_liabilities must be > 0")

    raw_shock_pct = weighted_sentiment_score * sensitivity
    shock_pct = max(-max_shock_pct, min(max_shock_pct, raw_shock_pct))

    total_assets = prior_total_assets * (1.0 + shock_pct)
    total_liabilities = prior_total_liabilities
    funded_ratio = total_assets / total_liabilities

    prior_funded_ratio = prior_total_assets / prior_total_liabilities

    return SimulatedFundedStatus(
        captured_at=captured_at,
        prior_total_assets=prior_total_assets,
        prior_total_liabilities=prior_total_liabilities,
        prior_funded_ratio=prior_funded_ratio,
        weighted_sentiment_score=weighted_sentiment_score,
        shock_pct=shock_pct,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        funded_ratio=funded_ratio,
    )


def recalculate_funded_status(
    *,
    db,
    lookback_hours: int = 24,
    sensitivity: float = 0.02,
    max_shock_pct: float = 0.02,
) -> SimulatedFundedStatus:
    """
    DB-backed recalculation:
    - avg sentiment by asset class over the lookback window
    - weighted by portfolio target_percentage
    - simulate funded-status update and insert a new funded_status_log row
    """
    # Local imports keep unit tests for pure functions lightweight.
    from sqlalchemy import func

    from . import models

    cutoff = datetime.utcnow() - timedelta(hours=lookback_hours)

    latest_funded = (
        db.query(models.FundedStatusLog)
        .order_by(models.FundedStatusLog.captured_at.desc())
        .first()
    )
    if latest_funded is None:
        raise ValueError("No funded_status_log baseline found in the database.")

    # Sentiment aggregation over recent window.
    sentiment_rows = (
        db.query(
            models.PortfolioTarget.asset_class.label("asset_class"),
            func.avg(models.MarketIntelligence.sentiment_score).label("avg_sentiment"),
        )
        .join(
            models.MarketIntelligence,
            models.MarketIntelligence.asset_class_id == models.PortfolioTarget.id,
        )
        .filter(models.MarketIntelligence.captured_at >= cutoff)
        .group_by(models.PortfolioTarget.asset_class)
        .all()
    )
    sentiment_by_asset_class = {
        row.asset_class: float(row.avg_sentiment) if row.avg_sentiment is not None else 0.0
        for row in sentiment_rows
    }

    # Portfolio weights (allocation split).
    target_rows = db.query(models.PortfolioTarget).all()
    weights_by_asset_class = {
        row.asset_class: float(row.target_percentage) for row in target_rows
    }

    weighted_score = compute_weighted_sentiment_score(
        sentiment_by_asset_class=sentiment_by_asset_class,
        weights_by_asset_class=weights_by_asset_class,
    )

    simulated = simulate_funded_status(
        prior_total_assets=float(latest_funded.total_assets),
        prior_total_liabilities=float(latest_funded.total_liabilities),
        weighted_sentiment_score=weighted_score,
        sensitivity=sensitivity,
        max_shock_pct=max_shock_pct,
    )

    db.add(
        models.FundedStatusLog(
            captured_at=simulated.captured_at,
            total_assets=simulated.total_assets,
            total_liabilities=simulated.total_liabilities,
            funded_ratio=simulated.funded_ratio,
        )
    )
    db.commit()

    return simulated


def get_latest_funded_status(db):
    from . import models

    return (
        db.query(models.FundedStatusLog)
        .order_by(models.FundedStatusLog.captured_at.desc())
        .first()
    )

