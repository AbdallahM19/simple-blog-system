"""/app/schemas.py"""

from pydantic import BaseModel
from datetime import datetime
from typing import Annotated, Optional, Union


class PostCreate(BaseModel):
    title: str
    content: str

class PostResponse(PostCreate):
    id: int
    user_id: int
    created_at: datetime
    edited_at: datetime

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    profile_image: Optional[str]
    role: str
    password: str
    access_token: str
