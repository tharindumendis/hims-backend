from fastapi import APIRouter
from services import mining_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/association-rules")
def get_association_rules(min_support: float = 0.05, min_confidence: float = 0.3):
    return mining_service.get_association_rules(min_support, min_confidence)

@router.get("/monthly-trend")
def get_monthly_consumption_trend():
    return mining_service.get_monthly_consumption_trend()
