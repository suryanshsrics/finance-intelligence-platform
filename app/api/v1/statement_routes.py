from typing import List
from fastapi import APIRouter, Depends, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from app.schemas.statement_schema import *
from app.services.statement_services import *
from app.database import get_db
from app.models.user_model import User
from app.auth.dependencies import get_current_user

router = APIRouter()

@router.post("/create-statement", response_model=StatementResponse, status_code=status.HTTP_201_CREATED)
def create_statement(statement: StatementCreate,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    return create_statement_service(statement, db, current_user.user_id)


@router.get("/statements", response_model=List[StatementResponse], status_code=status.HTTP_200_OK)
def get_statements(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_statements_service(current_user.user_id, db)


@router.get("/statement/{statement_id}", response_model=StatementResponse, status_code=status.HTTP_200_OK)
def get_statement_by_id(statement_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_statement_by_id_service(current_user.user_id, statement_id, db)


@router.post("/statements/upload")
def upload_statement(file: UploadFile = File(...),
                    password: str | None = Form(default=None),
                    db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    return statement_upload_service(current_user.user_id, file, password, db)
    