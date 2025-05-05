from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db
from ..auth import get_current_user, get_current_active_user
from .. import models

router = APIRouter()


@router.post("/", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    db_category = db.query(models.Category).filter(
        models.Category.id == transaction.category_id
    ).first()

    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return crud.create_transaction(db=db, transaction=transaction, user_id=current_user.id)


@router.get("/", response_model=list[schemas.Transaction])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    if category_id:
        db_category = db.query(models.Category).filter(
            models.Category.id == category_id
        ).first()
        if not db_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return crud.get_transactions_by_category(db,
                                                 category_id=category_id,
                                                 skip=skip,
                                                 limit=limit)
    elif start_date and end_date:
        if end_date < start_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
        return crud.get_transactions_by_period(
            db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit
        )
    else:
        return crud.get_transactions_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{transaction_id}", response_model=schemas.Transaction)
def read_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_active_user)
):
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found")
    if db_transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this transaction"
        )
    return db_transaction


@router.put("/{transaction_id}", response_model=schemas.Transaction)
def update_transaction(
        transaction_id: int,
        transaction: schemas.TransactionCreate,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_active_user)
):
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    if db_transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this transaction"
        )
    return crud.update_transaction(db=db, transaction_id=transaction_id, transaction=transaction)


@router.delete("/{transaction_id}")
def delete_transaction(
        transaction_id: int,
        db: Session = Depends(get_db),
        current_user: schemas.User = Depends(get_current_active_user)
):
    db_transaction = crud.get_transaction(db, transaction_id=transaction_id)
    if db_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    if db_transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this transaction"
        )
    return crud.delete_transaction(db=db, transaction_id=transaction_id)
