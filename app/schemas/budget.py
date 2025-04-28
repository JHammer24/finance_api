from pydantic import BaseModel

class BudgetBase(BaseModel):
    amount: float
    category_id: int

class BudgetCreate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True