from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db import Base, engine, get_db
from models import Expenses, ResponseExpenses, ResponseUsers, ReturnDuplicateResponse, Users
from schemas import ExpenseCreation, ExpenseUpdate, UserCreation, LoginInstance
from security import hash_password, verify_password


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/register", 
          status_code=201, 
          response_model=ResponseUsers
)
def create_user(data: UserCreation, db: Session = Depends(get_db)):
    user = Users(username=data.username, password=hash_password(data.password))
    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if db.query(Users).filter(Users.username == data.username).first() is not None:
            raise HTTPException(status_code=409, detail="Username already registered") from exc
        raise

    db.refresh(user)
    return user


@app.post("/login",
          status_code=200,
          #response model tbc
)
def login_user(data: LoginInstance, db: Session = Depends(get_db)):
    #check if data matches one of the records in the users table
    #check if username exists
    # existing_user = db.query(Users).filter(Users.username == data.username).first()

    # if existing_user.username != data.username or verify():
    #     raise HTTPException(
    #         status_code=404
    #         detail="Username and/or Password is invalid"
    #     )

    #if it exists, generate the jwt
    #if it doesnt exist, reject (future rate limiting idea ?)


@app.post(
    "/expenses",
    status_code=201,
    response_model=ResponseExpenses | ReturnDuplicateResponse,
    responses={200: {"model": ReturnDuplicateResponse}},
)
def create_expense(data: ExpenseCreation, response: Response, db: Session = Depends(get_db)):
    if db.get(Users, data.user_id) is None:
        raise HTTPException(status_code=404, detail="User not found")

    expense = Expenses(
        user_id=data.user_id,
        description=data.description,
        amount_cents=int(data.amount * 100),
        idempotency_key=data.idempotency_key,
    )
    db.add(expense)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        # The database checks the key even when two requests arrive together.
        if data.idempotency_key is not None:
            existing_expense = db.query(Expenses).filter(
                Expenses.user_id == data.user_id,
                Expenses.idempotency_key == data.idempotency_key,
            ).first()
            if existing_expense is not None:
                response.status_code = 200
                return ReturnDuplicateResponse(status="duplicate expense")
        raise

    db.refresh(expense)
    return expense


@app.patch("/expenses/{expense_id}", response_model=ResponseExpenses)
def modify_expense(expense_id: int, data: ExpenseUpdate, db: Session = Depends(get_db)):
    expense = db.get(Expenses, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    if data.description is not None:
        expense.description = data.description
    if data.amount is not None:
        expense.amount_cents = int(data.amount * 100)

    db.commit()
    db.refresh(expense)
    return expense


@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.get(Expenses, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")

    db.delete(expense)
    db.commit()
