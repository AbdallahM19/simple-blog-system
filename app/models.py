"""/app/models.py"""

from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime


class User(SQLModel, table=True):
    """User Model"""
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    access_token: str = Field(unique=True, index=True, nullable=False)
    username: str = Field(unique=True, index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    password: str = Field(nullable=False)
    role: str = Field(default="user")
    profile_image: Optional[str] = Field(default=None, nullable=True)


class Post(SQLModel, table=True):
    """Post Model"""
    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    user_id: int = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    edited_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
