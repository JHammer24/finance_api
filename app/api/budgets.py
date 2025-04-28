from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db
from ..auth import get_current_user

router = APIRouter()


@router.post("/", response_model=schemas.Budget)
def create_budget(
        budget: schemas.BudgetCreate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    # Check if budget for this category already exists
    existing_budget = crud.get_budget_by_category(db, user_id=current_user.id, category_id=budget.category_id)
    if existing_budget:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Budget for this category already exists")

    return crud.create_budget(db=db, budget=budget, user_id=current_user.id)


@router.get("/", response_model=list[schemas.Budget])
def read_budgets(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_user)
):
    return crud.get_budgets_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{budget_id}", response_model=schemas.Budget)
def read_budget(budget_id: int, db: Session = Depends(get_db)):
    db_budget = crud.get_budget(db, budget_id=budget_id)
    if db_budget is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return db_budget


@router.put("/{budget_id}", response_model=schemas.Budget)
def update_budget(
        budget_id: int,
        budget: schemas.BudgetCreate,
        db: Session = Depends(get_db)
):
    return crud.update_budget(db=db, budget_id=budget_id, budget=budget)


@router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    return crud.delete_budget(db=db, budget_id=budget_id)