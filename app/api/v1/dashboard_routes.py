# from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard_schema import DashboardSummaryResponse, CategoryBreakdownResponse, MonthlyTrendResponse, SpendingInsightsResponse
from app.services.dashboard_service import get_dashboard_summary, get_category_breakdown, get_monthly_trend, get_spending_insights

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary/{user_id}", response_model=DashboardSummaryResponse)
def dashboard_summary(user_id: int, db: Session = Depends(get_db)):
    return get_dashboard_summary(user_id=user_id, db=db)


@router.get("/category-breakdown/{user_id}", response_model=list[CategoryBreakdownResponse], status_code=status.HTTP_200_OK)
def category_breakdown(user_id: int, db: Session = Depends(get_db)):
    return get_category_breakdown(user_id=user_id, db=db)


@router.get("/monthly-trend/{user_id}", response_model=list[MonthlyTrendResponse], status_code=status.HTTP_200_OK)
def monthly_trend(user_id: int, db: Session = Depends(get_db)):
    return get_monthly_trend(user_id=user_id, db=db)

@router.get("/spending-insights/{user_id}", response_model=SpendingInsightsResponse, status_code=status.HTTP_200_OK)
def spending_insights(user_id: int, db: Session = Depends(get_db)):
    return get_spending_insights(user_id=user_id, db=db)