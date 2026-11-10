from datetime import datetime, timezone
from decimal import Decimal

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint

from db import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(128), nullable=False)


class Expenses(Base):
    __tablename__ = "expenses"
    __table_args__ = (UniqueConstraint("user_id", "idempotency_key"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String(200), nullable=False)
    amount_cents = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    idempotency_key = Column(Integer)

    @property
    def amount(self) -> Decimal:
        return Decimal(self.amount_cents).scaleb(-2)


class ResponseExpenses(BaseModel):
    id: int
    user_id: int
    description: str
    amount: Decimal
    created_at: datetime


class ResponseUsers(BaseModel):
    id: int
    username: str


class ReturnDuplicateResponse(BaseModel):
    status: str
