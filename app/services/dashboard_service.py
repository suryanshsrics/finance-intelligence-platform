from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.statement_model import Statement
from app.models.transaction_model import Transaction

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
