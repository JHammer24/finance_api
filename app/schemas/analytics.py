from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class CategorySpending(BaseModel):
    """Расходы по одной категории"""
    category_name: str
    amount: float

class BudgetComparison(BaseModel):
    """Сравнение расходов с бюджетом"""
    category_name: str
    spent: float
    budget: float
    overspending: float
    budget_percentage: float

class SpendingAnalysis(BaseModel):
    """Анализ расходов за период"""
    total_spent: float
    by_category: List[CategorySpending]
    budget_comparison: List[BudgetComparison]
    start_date: datetime
    end_date: datetime

class IncomeVsExpenses(BaseModel):
    """Сравнение доходов и расходов"""
    total_income: float
    total_expenses: float
    savings_rate: float  # в процентах
    period: str

class GoalProgress(BaseModel):
    """Прогресс по цели"""
    name: str
    progress: float  # в процентах
    days_left: int

class FinancialHealth(BaseModel):
    """Общая оценка финансового здоровья"""
    income_vs_expenses: IncomeVsExpenses
    goals_progress: List[GoalProgress]
    analysis_period: str