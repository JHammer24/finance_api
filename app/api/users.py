from fastapi import APIRouter, Depends
from .. import schemas
from ..auth.models import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=schemas.User)
async def read_user_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user
