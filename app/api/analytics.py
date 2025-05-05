from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..analytics.service import FinanceAnalyzer
from ..schemas.analytics import (
    SpendingAnalysis,
    IncomeVsExpenses,
    FinancialHealth
)
from ..auth.models import get_current_active_user

router = APIRouter(tags=["analytics"])


@router.get("/spending", response_model=SpendingAnalysis)
def analyze_spending(
        start_date: datetime,
        end_date: datetime,
        category_id: Optional[int] = None,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_active_user)
):
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date")

    analyzer = FinanceAnalyzer(db)
    return analyzer.get_spending_analysis(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id
    )


@router.get("/income-vs-expenses", response_model=IncomeVsExpenses)
def analyze_income_vs_expenses(
        start_date: datetime,
        end_date: datetime,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_active_user)
):
    analyzer = FinanceAnalyzer(db)
    return analyzer.get_income_vs_expenses(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/financial-health", response_model=FinancialHealth)
def get_financial_health(
        months: int = 3,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_active_user)
):
    if months <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Months must be positive")

    analyzer = FinanceAnalyzer(db)
    return analyzer.get_financial_health(
        user_id=current_user.id,
        months=months
    )
