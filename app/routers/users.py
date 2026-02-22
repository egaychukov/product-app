from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.models.users import User as UserModel
from app.schemas.users import UserCreate, User as UserSchema, RefreshTokenRequest
from app.db_depends import get_async_db, AsyncSession
from app.auth import hash_password, verify_password, create_access_token, create_refresh_token
from app.settings import settings


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    session: Annotated[AsyncSession, Depends(get_async_db)]
) -> UserSchema:
    result = await session.scalars(select(UserModel).where(UserModel.email == user.email))
    if result.first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered")

    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
        role=user.role
    )

    session.add(db_user)
    await session.commit()
    return db_user


@router.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_async_db)]
) -> dict[str, str]:

    user = await session.scalar(
        select(UserModel)
        .where(UserModel.email == form_data.username, UserModel.is_active == True))
    
    if not user or not verify_password(user.hashed_password, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"})
    
    data = {"sub": user.email, "role": user.role, "id": user.id}
    access_token, refresh_token = create_access_token(data), create_refresh_token(data)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token")
async def get_new_refresh_token(
    session: Annotated[AsyncSession, Depends(get_async_db)],
    refresh_request: RefreshTokenRequest
) -> dict[str, str]:
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not authorize"
    )
    
    try:
        payload = jwt.decode(refresh_request.refresh_token, 
                             settings.secret_key.get_secret_value(), [settings.algorithm])
    except jwt.PyJWTError:
        raise unauthorized_exception
    
    token_type, email = payload.get("token_type"), payload.get("sub")
    if token_type != "refresh" or email is None:
        raise unauthorized_exception
    
    user = await session.scalar(
        select(UserModel)
        .where(UserModel.is_active == True, UserModel.email == email)
    )
    if user is None:
        raise unauthorized_exception
    
    refresh_token = create_refresh_token({"sub": user.email, "role": user.role, "id": user.id})
    return {"refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh")
async def refresh_access_token(
    session: Annotated[AsyncSession, Depends(get_async_db)],
    refresh_request: RefreshTokenRequest
) -> dict[str, str]:
    invalid_token_exception = HTTPException(status.HTTP_401_UNAUTHORIZED,
                                            "could not validate token")

    try:
        payload = jwt.decode(refresh_request.refresh_token, settings.secret_key.get_secret_value(),
                             algorithms=[settings.algorithm])
    except jwt.PyJWTError:
        raise invalid_token_exception
    
    email, token_type = payload.get("sub"), payload.get("token_type")
    if email is None or token_type != "refresh":
        raise invalid_token_exception
    
    user = await session.scalar(
        select(UserModel)
        .where(UserModel.is_active == True, UserModel.email == email)
    )
    if user is None:
        raise invalid_token_exception
    
    access_token = create_access_token({"sub": user.email, "role": user.role, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
