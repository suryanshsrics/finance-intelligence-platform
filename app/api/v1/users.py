from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.schema import UserCreate, UserResponseSchema
from app.services.user_services import *
from app.database import get_db

router = APIRouter()

@router.post("/create-user", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = create_user_service(db, user)
        return new_user
    except HTTPException as http_exc:
        raise http_exc
