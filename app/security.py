"""/app/security.py"""

import os
import uuid
import hashlib

from typing import Optional
from sqlmodel import Session, select

from fastapi import Depends, Response, Cookie, UploadFile, HTTPException

from models import User
from database import get_session
from schemas import UserResponse


def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return get_password_hash(plain_password) == hashed_password


class CurrentData():
    def __init__(self):
        self.path_folder = f"{os.getcwd()}\images\profile"

    @staticmethod
    def _generate_token() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def _get_current_token(access_token: Optional[str] = Cookie(None)) -> Optional[str]:
        return access_token

    async def get_current_data(
        self,
        db: Session = Depends(get_session),
        access_token: Optional[str] = Depends(_get_current_token)
    ) -> Optional[UserResponse]:
        if not access_token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        current_user = db.exec(select(User).where(User.access_token == access_token)).first()
        if not current_user:
            raise HTTPException(status_code=401, detail="User not found")

        return current_user

    async def save_profile_image(self, file: UploadFile):
        """Save profile image"""
        if not os.path.exists(self.path_folder):
            os.makedirs(self.path_folder)

        file_location = f"{self.path_folder}\{file.filename}"
        with open(file_location, "wb") as f:
            f.write(await file.read())

        return file_location


current_class = CurrentData()
