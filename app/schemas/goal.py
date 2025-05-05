from datetime import datetime
from pydantic import BaseModel

class GoalBase(BaseModel):
    name: str
    target_amount: float
    deadline: datetime

class GoalCreate(GoalBase):
    pass

class Goal(GoalBase):
    id: int
    user_id: int
    current_amount: float

    class Config:
        from_attributes = True
