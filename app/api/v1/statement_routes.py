from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.statement_schema import *
from app.services.statement_services import *
from app.database import get_db

router = APIRouter()

@router.post("/create-statement", response_model=StatementResponse, status_code=status.HTTP_201_CREATED)
def create_statement(statement: StatementCreate, db: Session = Depends(get_db)):
    return create_statement_service(statement, db)


@router.get("/users/{user_id}/statements", response_model=List[StatementResponse], status_code=status.HTTP_200_OK)
def get_statements(user_id: int, db: Session = Depends(get_db)):
    return get_statements_service(user_id, db)


@router.get("/users/{user_id}/statement/{statement_id}", response_model=StatementResponse, status_code=status.HTTP_200_OK)
def get_statement_by_id(user_id: int, statement_id: int, db: Session = Depends(get_db)):
    return get_statement_by_id_service(user_id, statement_id, db)
