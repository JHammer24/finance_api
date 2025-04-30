from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas


class FinanceAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def get_spending_analysis(
            self,
            user_id: int,
            start_date: datetime,
            end_date: datetime,
            category_id: Optional[int] = None
    ) -> schemas.SpendingAnalysis:
        """
        Анализ расходов по категориям за период
        Возвращает:
        - Суммарные расходы
        - Распределение по категориям
        - Сравнение с бюджетами
        """
        # Получаем все транзакции пользователя за период
        transactions = self._get_transactions(user_id, start_date, end_date, "expense", category_id)

        # Анализируем данные
        total_spent = sum(t.amount for t in transactions)
        by_category = self._group_by_category(transactions)
        budget_comparison = self._compare_with_budgets(user_id, by_category)

        return schemas.SpendingAnalysis(
            total_spent=total_spent,
            by_category=by_category,
            budget_comparison=budget_comparison,
            start_date=start_date,
            end_date=end_date
        )

    def get_income_vs_expenses(
            self,
            user_id: int,
            start_date: datetime,
            end_date: datetime
    ) -> schemas.IncomeVsExpenses:
        """
        Сравнение доходов и расходов за период
        """
        incomes = self._get_transactions(user_id, start_date, end_date, "income")
        expenses = self._get_transactions(user_id, start_date, end_date, "expense")

        total_income = sum(t.amount for t in incomes)
        total_expenses = sum(t.amount for t in expenses)
        savings_rate = ((total_income - total_expenses) / total_income) * 100 if total_income > 0 else 0

        return schemas.IncomeVsExpenses(
            total_income=total_income,
            total_expenses=total_expenses,
            savings_rate=round(savings_rate, 2),
            period=f"{start_date.date()} - {end_date.date()}"
        )

    def get_financial_health(
            self,
            user_id: int,
            months: int = 3
    ) -> schemas.FinancialHealth:
        """
        Оценка финансового здоровья пользователя
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)

        # Анализ доходов/расходов
        income_expenses = self.get_income_vs_expenses(user_id, start_date, end_date)

        # Анализ целей
        goals = self.db.query(models.Goal).filter(
            models.Goal.user_id == user_id,
            models.Goal.deadline >= datetime.now()
        ).all()

        goals_progress = [
            schemas.GoalProgress(
                name=g.name,
                progress=round((g.current_amount / g.target_amount) * 100, 2),
                days_left=(g.deadline - datetime.now()).days
            ) for g in goals
        ]

        return schemas.FinancialHealth(
            income_vs_expenses=income_expenses,
            goals_progress=goals_progress,
            analysis_period=f"Last {months} months"
        )

    def _get_transactions(
            self,
            user_id: int,
            start_date: datetime,
            end_date: datetime,
            transaction_type: str,
            category_id: Optional[int] = None
    ) -> List[models.Transaction]:
        """Вспомогательный метод для получения транзакций"""
        query = self.db.query(models.Transaction).join(models.Category).filter(
            models.Transaction.user_id == user_id,
            models.Transaction.date >= start_date,
            models.Transaction.date <= end_date,
            models.Category.type == transaction_type
        )

        if category_id:
            query = query.filter(models.Transaction.category_id == category_id)

        return query.all()

    def _group_by_category(
            self,
            transactions: List[models.Transaction]
    ) -> List[schemas.CategorySpending]:
        """Группировка расходов по категориям"""
        from collections import defaultdict
        grouped = defaultdict(float)

        for t in transactions:
            grouped[t.category.name] += t.amount

        return [
            schemas.CategorySpending(category_name=name, amount=amount)
            for name, amount in grouped.items()
        ]

    def _compare_with_budgets(
            self,
            user_id: int,
            category_spending: List[schemas.CategorySpending]
    ) -> List[schemas.BudgetComparison]:
        """Сравнение расходов с установленными бюджетами"""
        comparisons = []

        for cs in category_spending:
            budget = self.db.query(models.Budget).join(models.Category).filter(
                models.Budget.user_id == user_id,
                models.Category.name == cs.category_name
            ).first()

            if budget:
                overspending = cs.amount - budget.amount if cs.amount > budget.amount else 0
                comparisons.append(
                    schemas.BudgetComparison(
                        category_name=cs.category_name,
                        spent=cs.amount,
                        budget=budget.amount,
                        overspending=overspending,
                        budget_percentage=round((cs.amount / budget.amount) * 100, 2)
                    )
                )

        return comparisons