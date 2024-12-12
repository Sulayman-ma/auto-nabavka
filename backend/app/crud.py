from typing import Any

from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


async def create_user(*, session: AsyncSession, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"password_hash": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


async def update_user(*, session: AsyncSession, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        password_hash = get_password_hash(password)
        extra_data["password_hash"] = password_hash
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
    return db_user


async def get_user_by_email(*, session: AsyncSession, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = await session.execute(statement)
    return session_user.scalars().first()


async def get_user_by_chat_id(*, session: AsyncSession, chat_id: int) -> User | None:
    statement = select(User).where(User.chat_id == chat_id)
    session_user = await session.execute(statement)
    return session_user.scalars().first()


async def get_task_active_users(*, session: AsyncSession) -> list[dict[str, int | str]] | None:
    # Fetch active users with active tasks only and return a list of dict with their chat IDs and URLs
    statement = select(User).where(
        User.is_active == True, 
        User.is_task_active == True
    )
    session_users = await session.execute(statement)
    return session_users.scalars().all()


async def authenticate(*, session: AsyncSession, email: str, password: str) -> User | None:
    db_user = await get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.password_hash):
        return None
    return db_user
