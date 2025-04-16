from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

class UserCreate(UserBase):
    email: EmailStr
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)

class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)

class UserInDBBase(UserBase):
    id: int
    email: EmailStr
    username: str
    created_at: datetime

    model_config = {
    "from_attributes": True
    }

class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None