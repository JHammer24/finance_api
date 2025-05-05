from fastapi import APIRouter, Depends, Body, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from .. import schemas, crud
from ..database import get_db
from ..auth.models import get_current_active_user

router = APIRouter()


@router.post("/", response_model=schemas.Goal)
def create_goal(
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    if goal.deadline < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Deadline cannot be in the past")
    return crud.create_goal(db=db, goal=goal, user_id=current_user.id)


@router.get("/", response_model=list[schemas.Goal])
def read_goals(
    active_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    if active_only:
        return crud.get_active_goals(db, user_id=current_user.id)
    return crud.get_goals_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{goal_id}", response_model=schemas.Goal)
def read_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    db_goal = crud.get_goal(db, goal_id=goal_id)
    if db_goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found")
    if db_goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this goal")
    return db_goal


@router.put("/{goal_id}", response_model=schemas.Goal)
def update_goal(
    goal_id: int,
    goal: schemas.GoalCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    db_goal = crud.get_goal(db, goal_id=goal_id)
    if db_goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found")
    if db_goal and db_goal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this goal")
    if goal.deadline < datetime.now():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Deadline cannot be in the past")
    return crud.update_goal(db=db, goal_id=goal_id, goal=goal)


@router.patch("/{goal_id}/add", response_model=schemas.Goal)
def add_to_goal(
    goal_id: int,
    amount: float = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    db_goal = crud.get_goal(db, goal_id=goal_id)
    if db_goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found")
    if db_goal and db_goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this goal")
    if amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Amount must be positive")
    return crud.update_goal_progress(db=db, goal_id=goal_id, amount=amount)


@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    db_goal = crud.get_goal(db, goal_id=goal_id)
    if db_goal is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Goal not found")
    if db_goal and db_goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this goal")
    return crud.delete_goal(db=db, goal_id=goal_id)