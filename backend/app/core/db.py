from sqlmodel import select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app import crud
from app.core.config import settings
from app.models import User, UserCreate

# Use an async engine
DATABASE_URL = str(settings.SQLALCHEMY_DATABASE_URI)
engine = create_async_engine(DATABASE_URL, pool_size=10)

# AsyncSession maker
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession
)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly


async def init_db() -> None:
    # NOTE: Tables should be created with Alembic migrations
    superusers = settings.SUPERUSERS
    async with AsyncSessionLocal() as session:
        for superuser in superusers:
            results = await session.execute(
                select(User).where(User.email == superuser)
            )
            user = results.scalars().first()
            if not user:
                user_in = UserCreate(
                    email=superuser,
                    password=settings.SUPERUSER_PASSWORD,
                    is_superuser=True,
                )
                await crud.create_user(session=session, user_create=user_in)
