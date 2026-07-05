from app.schemas.schema import UserCreate
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, insert
from fastapi import Depends, HTTPException
from app.models.user_model import User

def create_user_service(db:Session, user_data: UserCreate):
    # check if user exists in database
    stmt = select(User).where(User.email == user_data.email)
    existing_user = db.execute(stmt).scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # create new a user object
    new_user = User(user_name=user_data.user_name, email=user_data.email)

    # add user to session
    db.add(new_user)
    try:
        # commit transaction
        db.commit()

        # refresh object
        db.refresh(new_user)
    except Exception:
        db.rollback()
        raise


    return new_user