from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.schemas.statement_schema import *
from app.services.statement_services import *
from app.database import get_db

router = APIRouter()

@router.post("/create-statement", response_model=StatementResponse, status_code=status.HTTP_201_CREATED)
def create_statement(statement: StatementCreate, db: Session = Depends(get_db)):
    return create_statement_service(statement, db) 