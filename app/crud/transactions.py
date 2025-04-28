from sqlalchemy.orm import Session
from datetime import datetime
from .. import models, schemas

def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

def get_transactions_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_transactions_by_category(db: Session, category_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Transaction)
        .filter(models.Transaction.category_id == category_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def create_transaction(db: Session, transaction: schemas.TransactionCreate, user_id: int):
    db_transaction = models.Transaction(**transaction.model_dump(), user_id=user_id)
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def update_transaction(db: Session, transaction_id: int, transaction: schemas.TransactionCreate):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_transaction:
        for key, value in transaction.model_dump().items():
            setattr(db_transaction, key, value)
        db.commit()
        db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
    return db_transaction

def get_transactions_by_period(
    db: Session,
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100
):
    return (
        db.query(models.Transaction)
        .filter(
            models.Transaction.user_id == user_id,
            models.Transaction.date >= start_date,
            models.Transaction.date <= end_date
        )
        .offset(skip)
        .limit(limit)
        .all()
    )