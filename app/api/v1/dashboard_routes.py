# from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard_schema import DashboardSummaryResponse, CategoryBreakdownResponse, MonthlyTrendResponse, SpendingInsightsResponse
from app.services.dashboard_service import get_dashboard_summary, get_category_breakdown, get_monthly_trend, get_spending_insights
from app.models.user_model import User
from app.auth.dependencies import get_current_user


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_dashboard_summary(user_id=current_user.user_id, db=db)


@router.get("/category-breakdown", response_model=list[CategoryBreakdownResponse], status_code=status.HTTP_200_OK)
def category_breakdown(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_category_breakdown(user_id=current_user.user_id, db=db)


@router.get("/monthly-trend", response_model=list[MonthlyTrendResponse], status_code=status.HTTP_200_OK)
def monthly_trend(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_monthly_trend(user_id=current_user.user_id, db=db)

@router.get("/spending-insights", response_model=SpendingInsightsResponse, status_code=status.HTTP_200_OK)
def spending_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_spending_insights(user_id=current_user.user_id, db=db)