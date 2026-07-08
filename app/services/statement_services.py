from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.statement_model import Statement
from app.models.user_model import User
from app.schemas.statement_schema import StatementCreate
from app.database import get_db

def create_statement_service(statement: StatementCreate, db: Session):
    stmt = select(User).where(User.user_id == statement.user_id)
    user = db.execute(stmt).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    
    if statement.statement_start_date > statement.statement_end_date:
        raise HTTPException(status_code=400, detail="Start date cannot be after the end date. ")
    
    if not statement.file_name or not statement.file_name.strip():
        raise HTTPException(status_code=400, detail="file_name cannot be empty")
    
    new_statement = Statement(user_id = statement.user_id, file_name = statement.file_name, bank_name = statement.bank_name
    , account_number_last4 = statement.account_number_last4, statement_start_date = statement.statement_start_date, statement_end_date = statement.statement_end_date)

    db.add(new_statement)
    try:
        db.commit()
        db.refresh(new_statement)
    except Exception:
        db.rollback()
        raise

    return new_statement

def get_statements_service(user_id: int, db: Session):
    stmt = select(User).where(User.user_id == user_id)
    user = db.execute(stmt).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    
    stmt_statement = select(Statement).where(Statement.user_id == user_id)
    statements = db.execute(stmt_statement).scalars().all()
    return statements

def get_statement_by_id_service(user_id: int, statement_id: int, db: Session):
    stmt = select(User).where(User.user_id == user_id)
    user = db.execute(stmt).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    stmt2 = select(Statement).where(Statement.user_id == user_id, 
                                    Statement.statement_id == statement_id)
    required_statement = db.execute(stmt2).scalar_one_or_none()
    if required_statement is None:
        raise HTTPException(status_code=404, detail=f"No statement with id: {statement_id}")
    return required_statement