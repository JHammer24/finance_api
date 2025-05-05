from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TransactionBase(BaseModel):
    amount: float
    description: Optional[str] = None
    date: Optional[datetime] = None
    category_id: int

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
