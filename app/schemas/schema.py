from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class UserCreate(BaseModel):
    user_name: str = Field(min_length=6, max_length=50)
    email: EmailStr

class UserResponseSchema(BaseModel):
    user_id: int
    user_name: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True