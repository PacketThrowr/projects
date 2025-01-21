from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import async_session_maker
from app.models.user import User
from fastapi_users.db import SQLAlchemyUserDatabase

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_db)):
    user_db = SQLAlchemyUserDatabase(session, User)

    # Add support for username lookup
    async def get_by_username(username: str):
        query = select(User).where(User.username == username)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    setattr(user_db, "get_by_username", get_by_username)
    return user_db

async def get_user_manager(user_db=Depends(get_user_db)):
    yield CustomUserManager(user_db)