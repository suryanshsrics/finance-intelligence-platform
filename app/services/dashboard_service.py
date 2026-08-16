from sqlalchemy import select, func, case
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.statement_model import Statement
from app.models.transaction_model import Transaction
from app.models.user_model import User


def get_user_or_404(user_id: int, db: Session, detail: str = "User not found") -> User:
    stmt = select(User).where(User.user_id == user_id)
    user = db.execute(stmt).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail=detail)
    return user

def get_dashboard_summary(user_id: int, db: Session):

    total_statements = db.scalar(select(func.count()).select_from(Statement).where(Statement.user_id == user_id))

    total_transactions = db.scalar(select(func.count()).select_from(Transaction).join(Statement).where(Statement.user_id == user_id))

    total_income = db.scalar(select(func.sum(Transaction.amount)).join(Statement).where(Statement.user_id == user_id, Transaction.transaction_type == 'CREDIT')) or 0

    total_expenditure = db.scalar(select(func.sum(Transaction.amount)).join(Statement).where(Statement.user_id == user_id, Transaction.transaction_type == 'DEBIT')) or 0

    net_savings = total_income - total_expenditure

    return{
        "total_income": total_income,
        "total_expense": total_expenditure,
        "net_savings": net_savings,
        "total_transactions": total_transactions,
        "total_statements": total_statements
    }


def get_category_breakdown(user_id: int, db: Session):
    user = get_user_or_404(user_id, db, detail='This user does not exist')

    result = db.execute(
    select(
        Transaction.category,
        func.sum(Transaction.amount).label("amount"),
    )
    .join(Statement)
    .where(
        Statement.user_id == user_id,
        Transaction.transaction_type == "DEBIT",
    )
    .group_by(Transaction.category)
    .order_by(func.sum(Transaction.amount).desc())
    ).all()

    return[
        {
            "category": row.category,
            "amount": row.amount
        }
        for row in result
    ]

def get_monthly_trend(user_id: int, db: Session):
    user = get_user_or_404(user_id=user_id, db=db, detail="This user does not exist")
    month = func.to_char(Transaction.transaction_date, "YYYY-MM").label("month")
    query = select(
        month, func.sum(
            case(
                (
                Transaction.transaction_type == 'CREDIT',
                Transaction.amount
            ),
            else_=0
            )
        ).label("income"), func.sum(
            case(
                (
                    Transaction.transaction_type == 'DEBIT',
                    Transaction.amount
                ),
                else_=0
            )
        ).label("expense")
    ).join(Statement).where(Statement.user_id == user_id).group_by(month).order_by(month)

    result = db.execute(query).all()

    return[
        {
            "month": row.month,
            "income": row.income,
            "expense": row.expense
        }
        for row in result
    ]

def highest_spending_category(user_id: int, db: Session):
    get_user_or_404(user_id=user_id, db=db, detail="This user does not exist")
    result = db.execute(select(Transaction.category, func.sum(Transaction.amount).label("highest_spent_amount"))
                        .join(Statement)
                        .where(Statement.user_id == user_id, Transaction.transaction_type == 'DEBIT')
                        .group_by(Transaction.category).order_by(func.sum(Transaction.amount).desc()).limit(1)).first()

    if not result:
        return {
            "highest_spending_category": None,
            "highest_spent_amount": 0.0
        }
    
    return {
        "highest_spending_category": result.category,
        "highest_spent_amount": float(result.highest_spent_amount)
    }

def average_monthly_expense(user_id: int, db: Session):
    get_user_or_404(user_id=user_id, db=db, detail="This user does not exist")
    month = func.to_char(Transaction.transaction_date, "YYYY-MM").label("month")
    monthly_expense_subquery = select(month, func.sum(Transaction.amount).label("monthly_expense")).join(Statement).where(Statement.user_id == user_id, Transaction.transaction_type == 'DEBIT').group_by(month).subquery()

    average_monthly_expense = db.execute(select(func.avg(monthly_expense_subquery.c.monthly_expense))).scalar_one()
    if average_monthly_expense is None:
        return {"average_monthly_expense": 0}

    return {"average_monthly_expense": average_monthly_expense}

def largest_transaction(user_id: int, db: Session):
    get_user_or_404(user_id=user_id, db=db, detail="This user does not exist")
    result = db.execute(select(Transaction.amount, Transaction.description, Transaction.transaction_date, Transaction.category).join(Statement)
    .where(Statement.user_id == user_id, Transaction.transaction_type == 'DEBIT')
    .order_by(Transaction.amount.desc()).limit(1)).first()

    if result is None:
        return {"amount": 0.0}
    return {
        "amount": result.amount,
        "description": result.description,
        "transaction_date": result.transaction_date,
        "category": result.category
    }

def get_spending_insights(user_id: int, db: Session):
    highest_category = highest_spending_category(user_id=user_id, db=db)
    average_expense = average_monthly_expense(user_id=user_id, db=db)
    largest_debit = largest_transaction(user_id=user_id, db=db)
    largest_tx = {
                "largest_debit_amount": largest_debit["amount"],
                "description": largest_debit['description'],
                "transaction_date": largest_debit['transaction_date'],
                "category": largest_debit['category']
            }

    return {
        "highest_spending_category": highest_category["highest_spending_category"],
        "highest_spent_amount": highest_category["highest_spent_amount"],
        "average_monthly_expense": average_expense["average_monthly_expense"],
        "largest_transaction": largest_tx
    }