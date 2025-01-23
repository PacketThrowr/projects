from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()

async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    is_active: bool = True,
    is_superuser: bool = False,
    is_verified: bool = False,
):
    new_user = User(
        username=username,
        email=email,
        hashed_password=password,  # Ensure this is hashed
        is_active=is_active,
        is_superuser=is_superuser,
        is_verified=is_verified,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    return user

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()

async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate):
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        raise ValueError("User not found")

    for key, value in user_update.dict(exclude_unset=True).items():
        if key == "password" and value:  # Hash the password if it's in the payload
            hashed_password = hash_password(value)
            setattr(db_user, "hashed_password", hashed_password)
        else:
            setattr(db_user, key, value)

    await db.commit()
    await db.refresh(db_user)
    return db_user

async def delete_user(db: AsyncSession, user_id: int):
    db_user = await get_user_by_id(db, user_id)
    if not db_user:
        raise ValueError("User not found")

    await db.delete(db_user)
    await db.commit()

async def get_all_users(db: AsyncSession) -> list[User]:
    """Fetch all users, including is_active, is_superuser, and is_verified."""
    result = await db.execute(select(User))
    return result.scalars().all()