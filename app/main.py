from fastapi import FastAPI
from .database import engine
from . import models
from .api import (
    users,
    categories,
    transactions,
    budgets,
    goals,
    analytics
)
from .auth.router import router as auth_router

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router, prefix="/auth")
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(categories.router, prefix="/categories", tags=["categories"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(budgets.router, prefix="/budgets", tags=["budgets"])
app.include_router(goals.router, prefix="/goals", tags=["goals"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

@app.get("/")
def read_root():
    return {"message": "Personal Finance Management System"}
