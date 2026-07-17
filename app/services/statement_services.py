from fastapi import Depends, HTTPException, UploadFile
from decimal import Decimal
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.statement_model import Statement
from app.models.transaction_model import Transaction
from app.models.user_model import User
from app.schemas.statement_schema import StatementCreate
from app.parsers.statement_parser import *
from app.parsers.parser_factory import *
from app.database import get_db


def check_existing_statement(
    db: Session,
    user_id: int,
    account_last4: str,
    start_date,
    end_date,
):
    existing_statements = db.execute(
        select(Statement).where(
            Statement.user_id == user_id,
            Statement.account_number_last4 == account_last4,
        )
    ).scalars().all()

    statements_to_replace = []

    for existing in existing_statements:

        # Case 1: Exact duplicate
        if (
            existing.statement_start_date == start_date
            and existing.statement_end_date == end_date
        ):
            return "DUPLICATE", None

        # Check whether date ranges overlap
        overlap = (
            existing.statement_start_date <= end_date
            and existing.statement_end_date >= start_date
        )

        # No overlap → ignore this statement
        if not overlap:
            continue

        # Case 2: New statement completely covers existing statement
        if (
            start_date <= existing.statement_start_date
            and end_date >= existing.statement_end_date
        ):
            statements_to_replace.append(existing)
            continue

        # Case 3: New statement is completely inside an existing statement
        if (
            start_date >= existing.statement_start_date
            and end_date <= existing.statement_end_date
        ):
            return "REJECT", None

        # Case 4: Partial overlap
        return "REJECT", None

    # Finished checking every existing statement
    if statements_to_replace:
        return "REPLACE", statements_to_replace

    return "NEW", None

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

def statement_upload_service(user_id: int, file: UploadFile,
                             password: str | None, db: Session):
    
    # check if the user exists
    stmt = select(User).where(User.user_id == user_id)
    user = db.execute(stmt).scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=404, detail="User does not exist.")
    
    # check if the uploaded file is a pdf
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail='Only pdf files are allowed.')
    
    # check for empty file name
    if not file.filename:
        raise HTTPException(status_code=400, detail='No file selected.')
    
    try:
        parsed_pdf = extract_text_from_pdf(
            file.file,
            password=password
        )

        bank = detect_bank(parsed_pdf["raw_text"])
        parser = get_parser(bank_name=bank)

        parsed_statement = parser.parse_statement(parsed_pdf["raw_text"])
        
        metadata = parsed_statement["metadata"]
        transactions = parsed_statement['transactions']

        statement_start_date = datetime.strptime(
            metadata["statement_start_date"],
            "%d-%m-%Y"
        ).date()

        statement_end_date = datetime.strptime(
            metadata["statement_end_date"],
            "%d-%m-%Y"
        ).date()

        account_number_last4 = metadata["account_number"][-4:]

        action, existing_statements = check_existing_statement(db=db, user_id=user_id, account_last4=account_number_last4, start_date=statement_start_date, end_date=statement_end_date)

        if action == 'DUPLICATE':
            raise HTTPException(status_code=409, detail='This statement has already been uploaded.')
        
        elif action == 'REPLACE':
            for statement in existing_statements or []:
                db.delete(statement)
            db.flush()

        elif action == 'REJECT':
            raise HTTPException(status_code=409, detail='This statement overlaps with an existing statement.')

        statement = Statement(
            user_id=user_id,
            file_name=file.filename,
            bank_name=metadata['bank_name'],
            account_number_last4=metadata['account_number'][-4:],
            statement_start_date=statement_start_date,
            statement_end_date=statement_end_date,
            total_transactions=len(transactions)
        )

        db.add(statement)
        db.flush()

        transaction_models = []
        for transaction in transactions:
            model = Transaction(
                statement_id=statement.statement_id,
                transaction_date=datetime.strptime(transaction['transaction_date'], "%d/%m/%Y").date(),
                description=transaction['description'],
                amount=Decimal(transaction['amount']),
                transaction_type=transaction['transaction_type'],
                balance_after_transaction=Decimal(transaction['balance'])
            )
            transaction_models.append(model)

        db.add_all(transaction_models)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise

        return {
        "message": "Statement uploaded successfully.",
        "statement_id": statement.statement_id,
        "bank_name": statement.bank_name,
        "transactions_imported": len(transaction_models),
        }


    except PdfPasswordRequiredError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except PdfIncorrectPasswordError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except PdfParsingError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )