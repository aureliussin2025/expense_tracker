from decimal import Decimal

from pydantic import BaseModel, Field


class UserCreation(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=128)


class ExpenseCreation(BaseModel):
    user_id: int = Field(gt=0)
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, max_digits=9, decimal_places=2)
    idempotency_key: int | None = Field(default=None, ge=1, le=2_147_483_647)


class ExpenseUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=200)
    amount: Decimal | None = Field(default=None, gt=0, max_digits=9, decimal_places=2)

class LoginInstance(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=128)