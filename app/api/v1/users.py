from typing import List
from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session
from app.schemas.schema import UserCreate, UserResponseSchema, UserListResponseSchema, UserUpdate
from app.services.user_services import *
from app.database import get_db

router = APIRouter()

@router.post("/create-user", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user_service(db, user)


@router.get("/user-list", response_model=List[UserListResponseSchema], status_code=status.HTTP_200_OK)
def get_user_list(db: Session = Depends(get_db)):
    return user_list_service(db)
    

@router.get("/get-user-by-id", response_model=UserResponseSchema, status_code=status.HTTP_200_OK)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    return user_by_id_service(user_id, db)


@router.put("/update-user", response_model=UserResponseSchema, status_code=status.HTTP_200_OK)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    return user_update_service(user_id, user_update, db)


@router.delete("/delete-user", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return user_delete_service(user_id, db)