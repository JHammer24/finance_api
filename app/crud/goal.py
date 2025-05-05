from datetime import datetime
from sqlalchemy.orm import Session
from .. import models, schemas

def get_goal(db: Session, goal_id: int):
    return db.query(models.Goal).filter(models.Goal.id == goal_id).first()

def get_goals_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Goal)
        .filter(models.Goal.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_active_goals(db: Session, user_id: int, current_date: datetime = datetime.now()):
    return (
        db.query(models.Goal)
        .filter(
            models.Goal.user_id == user_id,
            models.Goal.deadline >= current_date
        )
        .all()
    )

def create_goal(db: Session, goal: schemas.GoalCreate, user_id: int):
    db_goal = models.Goal(**goal.model_dump(), user_id=user_id)
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal

def update_goal(db: Session, goal_id: int, goal: schemas.GoalCreate):
    db_goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if db_goal:
        for key, value in goal.model_dump().items():
            setattr(db_goal, key, value)
        db.commit()
        db.refresh(db_goal)
    return db_goal

def delete_goal(db: Session, goal_id: int):
    db_goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if db_goal:
        db.delete(db_goal)
        db.commit()
    return db_goal

def update_goal_progress(db: Session, goal_id: int, amount: float):
    db_goal = db.query(models.Goal).filter(models.Goal.id == goal_id).first()
    if db_goal:
        db_goal.current_amount += amount
        db.commit()
        db.refresh(db_goal)
    return db_goal
