from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, crud
from ..database import get_db
from ..auth.models import get_current_active_user

router = APIRouter()


@router.post("/", response_model=schemas.Category)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    if category.type not in ('income', 'expense'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category type must be income or expense")
    return crud.create_category(db=db, category=category)


@router.get("/", response_model=list[schemas.Category])
def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    return crud.get_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=schemas.Category)
def read_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found")
    return db_category


@router.put("/{category_id}", response_model=schemas.Category)
def update_category(
    category_id: int,
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    if category.type not in ('income', 'expense'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category type must be income or expense"
        )

    return crud.update_category(db=db, category_id=category_id, category=category)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    crud.delete_category(db=db, category_id=category_id)