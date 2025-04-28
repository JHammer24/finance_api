from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from ..database import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(Enum('income', 'expense', name='category_type'))

    transactions = relationship("Transaction", back_populates="category")
    budgets = relationship("Budget", back_populates="category")