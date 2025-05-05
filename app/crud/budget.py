from sqlalchemy.orm import Session
from .. import models, schemas

def get_budget(db: Session, budget_id: int):
    return db.query(models.Budget).filter(models.Budget.id == budget_id).first()

def get_budgets_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Budget)
        .filter(models.Budget.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_budget_by_category(db: Session, user_id: int, category_id: int):
    return (
        db.query(models.Budget)
        .filter(
            models.Budget.user_id == user_id,
            models.Budget.category_id == category_id
        )
        .first()
    )

def create_budget(db: Session, budget: schemas.BudgetCreate, user_id: int):
    db_budget = models.Budget(**budget.model_dump(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget

def update_budget(db: Session, budget_id: int, budget: schemas.BudgetCreate):
    db_budget = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    if db_budget:
        for key, value in budget.model_dump().items():
            setattr(db_budget, key, value)
        db.commit()
        db.refresh(db_budget)
    return db_budget

def delete_budget(db: Session, budget_id: int):
    db_budget = db.query(models.Budget).filter(models.Budget.id == budget_id).first()
    if db_budget:
        db.delete(db_budget)
        db.commit()
    return db_budget
