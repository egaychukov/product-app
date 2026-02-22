from typing import Annotated

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8)]
    role: Annotated[str, Field(default="buyer", pattern="^(buyer|seller|admin)$")]


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    role: str
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str
