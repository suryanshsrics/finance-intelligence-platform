from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard_schema import DashboardSummaryResponse
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary/{user_id}", response_model=DashboardSummaryResponse)
def dashboard_summary(user_id: int, db: Session = Depends(get_db)):
    return get_dashboard_summary(user_id=user_id, db=db)