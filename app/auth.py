from typing import Any, Annotated
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy import select

from app.settings import settings
from app.db_depends import AsyncSession, get_async_db
from app.schemas.users import User
from app.models.users import User as UserModel


context = CryptContext(schemes=["argon2"])
oauth_schema = OAuth2PasswordBearer(tokenUrl="users/token")


def hash_password(password: str) -> str:
    return context.hash(password)


def verify_password(hash: str, password: str) -> bool:
    return context.verify(password, hash)


def create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()

    to_encode.update(
        {
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.access_token_ttl),
            "token_type": "access",
        }
    )

    return jwt.encode(
        to_encode, settings.secret_key.get_secret_value(), settings.algorithm
    )


def create_refresh_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()

    to_encode.update(
        {
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=settings.refresh_token_ttl),
            "token_type": "refresh",
        }
    )

    return jwt.encode(
        to_encode, settings.secret_key.get_secret_value(), settings.algorithm
    )


async def get_current_user(
    session: Annotated[AsyncSession, Depends(get_async_db)],
    token: Annotated[str, Depends(oauth_schema)],
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
        )

        token_type = payload.get("token_type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="could not use refresh token to gain access",
            )

        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="could not authorize"
            )

        user = await session.scalar(
            select(UserModel).where(
                UserModel.is_active == True, UserModel.email == email
            )
        )

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="could not authorize"
            )

        return user

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="could not authorize"
        )


def get_current_role(role: str):
    def dependency(current_user: Annotated[User, Depends(get_current_user)]):
        if current_user.role != role:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail=f"{role} role needed to perform this action",
            )
        return current_user

    return dependency
