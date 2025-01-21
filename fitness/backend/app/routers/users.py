from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.schemas.user import UserCreate, UserResponse
from app.crud import create_user, get_user_by_username
from app.utils.security import hash_password

router = APIRouter()


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


@router.post("/users/", response_model=UserResponse)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if the username already exists
    db_user = await get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the user's password
    hashed_password = hash_password(user.password)

    # Create the new user
    return await create_user(db, username=user.username, email=user.email, password=hashed_password)
