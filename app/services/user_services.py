from app.schemas.schema import UserCreate, UserUpdate
from app.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select, insert
from fastapi import Depends, HTTPException
from app.models.user_model import User


def get_user_or_404(db: Session, user_id: int, detail: str = "User not found.") -> User:
    stmt = select(User).where(User.user_id == user_id)
    user = db.execute(stmt).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail=detail)
    return user

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

def user_list_service(db: Session):
    stmt = select(User)
    users = db.execute(stmt).scalars().all()
    return users

def user_by_id_service(id: int, db: Session):
    return get_user_or_404(db, id)
    
def user_update_service(id: int, user_updated: UserUpdate, db:Session):
    user = get_user_or_404(db, id, detail="This user does not exist. ")
    
    email_new = user_updated.email
    check_duplicate_email_stmt = select(User).where(User.email == email_new, 
                                                    User.user_id != id)
    existing_email = db.execute(check_duplicate_email_stmt).scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=409, detail="User with provided email already exists")
    
    # Update the ORM object
    user.user_name = user_updated.user_name
    user.email = user_updated.email

    db.commit()
    db.refresh(user)

    return user

def user_delete_service(id: int, db: Session):
    user = get_user_or_404(db, id)
    
    db.delete(user)
    db.commit()
