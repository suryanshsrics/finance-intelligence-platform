from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime

class UserCreate(BaseModel):
    user_name: str = Field(min_length=1, max_length=50)
    email: EmailStr

class UserResponseSchema(BaseModel):
    user_id: int
    user_name: str
    email: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserListResponseSchema(BaseModel):
    user_id: int
    user_name: str
    email: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    user_name: str = Field(min_length=1, max_length=50)
    email: EmailStr