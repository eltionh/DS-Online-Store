from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=4, max_length=80)


class UserAdminCreate(UserCreate):
    role: str = Field(pattern="^(admin|user)$")


class UserUpdate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: Optional[str] = Field(default=None, min_length=4, max_length=80)
    role: str = Field(pattern="^(admin|user)$")


class User(BaseModel):
    id: int
    username: str
    role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    role: str
