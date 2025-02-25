"""/app/routes/user_api.py"""

from re import match
from typing import Annotated, Optional
from sqlmodel import Session, select, update

from fastapi import APIRouter, Form, HTTPException, Response, Depends, File, UploadFile
from fastapi.responses import FileResponse

from models import User
from database import get_session
from schemas import UserLogin, UserRegister, UserResponse
from security import get_password_hash, verify_password, current_class


route = APIRouter(prefix="/auth", tags=["Auth"])

EMAIL_REGEX = r"^([a-z]+)((([a-z]+)|(_[a-z]+))?(([0-9]+)|(_[0-9]+))?)*@([a-z]+).([a-z]+)$"


@route.post("/login", response_model=UserResponse)
async def login(
    user: UserLogin,
    response: Response,
    db: Session = Depends(get_session),
):
    """Login"""
    current_user = None
    try:
        if match(EMAIL_REGEX, user.username):
            current_user = db.exec(select(User).where(User.email == user.username)).first()
        else:
            current_user = db.exec(select(User).where(User.username == user.username)).first()

        if not current_user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(user.password, current_user.password):
            raise HTTPException(status_code=401, detail="Invalid password")

        token = current_class._generate_token()

        response.set_cookie(
            key="access_token",
            value=token,
            max_age=3600*24*7
        )

        current_user.access_token = token
        db.commit()
        db.refresh(current_user)

        return current_user
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@route.post("/register", response_model=UserResponse)
async def read_register(
    user: UserRegister,
    response: Response,
    db: Session = Depends(get_session)
):
    """Register"""
    current_user = None

    try:
        if match(EMAIL_REGEX, user.email):
            current_user = db.exec(select(User).where(User.email == user.email)).first()
        else:
            current_user = db.exec(select(User).where(User.username == user.username)).first()

        if current_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        hash_pass = get_password_hash(user.password)

        token = current_class._generate_token()

        current_user = User(
            **user.model_dump(exclude={"password"}),
            password=hash_pass,
            access_token=token
        )

        response.set_cookie(
            key="access_token",
            value=token,
            max_age=3600*24*7
        )

        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        return current_user
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@route.get("/profile-image")
async def read_profile_image(
    db: Session = Depends(get_session),
    token: Optional[str] = Depends(current_class._get_current_token)
):
    """Profile Image"""
    if not token:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

    user = db.exec(select(User).where(User.access_token == token)).first()

    if not user or not user.profile_image:
        raise HTTPException(status_code=404, detail="Profile image not found")

    return FileResponse(user.profile_image, media_type="image/jpeg")

@route.post("/profile-image")
async def read_profile_image(
    image: Annotated[UploadFile, File(...)],
    db: Session = Depends(get_session),
    token: Optional[str] = Depends(current_class._get_current_token)
) -> str:
    """Profile Image"""
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    location_file = await current_class.save_profile_image(file=image)

    user = db.exec(select(User).where(User.access_token == token)).first()

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user.profile_image = location_file
    db.commit()
    db.refresh(user)

    return FileResponse(location_file, media_type="image/jpeg")
