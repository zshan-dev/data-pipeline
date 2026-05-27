from datetime import datetime

from sqlalchemy.orm import Session

from . import models

# HOOPP long-term asset mix as of Dec 31, 2024 (published percentages; sum > 100%
# due to -11% balance-sheet borrowing allocated across categories).
# Private equity is not broken out separately in this public mix — equities
# includes public equities per HOOPP's footnote, so we do not invent a PE row.
DEFAULT_PORTFOLIO_TARGETS = [
    {"asset_class": "Equities", "target_percentage": 0.38, "risk_level": "High"},
    {"asset_class": "Nominal Bonds", "target_percentage": 0.23, "risk_level": "Low"},
    {"asset_class": "Real Return Bonds", "target_percentage": 0.19, "risk_level": "Low"},
    {"asset_class": "Real Estate", "target_percentage": 0.18, "risk_level": "High"},
    {"asset_class": "Infrastructure", "target_percentage": 0.07, "risk_level": "Medium"},
    {"asset_class": "Credit", "target_percentage": 0.06, "risk_level": "Medium"},
]

# HOOPP investment performance snapshot, Dec 31, 2024. Dollar amounts in billions.
FUNDED_STATUS_SNAPSHOT = {
    "captured_at": datetime(2024, 12, 31),
    "total_assets": 123.0,
    "total_liabilities": round(123.0 / 1.11, 2),
    "funded_ratio": 1.11,
}


def seed_portfolio_targets(db: Session) -> int:
    """Insert default portfolio targets if they do not already exist."""
    inserted = 0
    for row in DEFAULT_PORTFOLIO_TARGETS:
        exists = (
            db.query(models.PortfolioTarget)
            .filter(models.PortfolioTarget.asset_class == row["asset_class"])
            .first()
        )
        if exists:
            continue
        db.add(models.PortfolioTarget(**row))
        inserted += 1

    if inserted:
        db.commit()
    return inserted


def seed_funded_status(db: Session) -> int:
    """Insert the baseline funded-status snapshot if not already present."""
    exists = (
        db.query(models.FundedStatusLog)
        .filter(models.FundedStatusLog.captured_at == FUNDED_STATUS_SNAPSHOT["captured_at"])
        .first()
    )
    if exists:
        return 0

    db.add(models.FundedStatusLog(**FUNDED_STATUS_SNAPSHOT))
    db.commit()
    return 1
