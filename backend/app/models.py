import uuid

from pydantic import EmailStr
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, BigInteger


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = Field(default=True)
    is_superuser: bool = False


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password_hash: str
    mobili_url: str | None = Field(default=None)
    chat_id: int | None = Field(default=None, sa_column=Column(BigInteger, nullable=True, index=True))
    is_task_active: bool = Field(default=False)
    previous_ads: str = Field(default='[]')


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)
    is_task_active: bool | None = Field(default=None)
    mobili_url: str | None = Field(default=None)
    chat_id: int | None = Field(default=None, sa_column=Column(BigInteger, nullable=True, index=True))
    is_active: bool = Field(default=True)
    previous_ads: str = Field(default=None)


class UserUpdateMe(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    chat_id: int | None
    mobili_url: str | None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class TaskUserResponse(SQLModel):
    users: list[dict[str, int | str]]


class TaskRequest(SQLModel):
    celery_auth: str


class AdsRequest(TaskRequest):
    chat_id: int
    ads: list[str]


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None

# Generic message
class Message(SQLModel):
    message: str
