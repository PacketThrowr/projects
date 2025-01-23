from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app import crud
from app.utils.security import hash_password
from app.auth.backend import current_active_user, is_superuser
from app.utils import hash_password
from app.models.user import User

router = APIRouter()


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

@router.get("/users/", response_model=list[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    if is_superuser(user):  # Check if the user is a superuser
        return await crud.get_all_users(db)  # Return all users
    else:
        # Return only the authenticated user's information
        return [UserResponse.from_orm(user)]

@router.post("/users/", response_model=UserResponse)
async def create_new_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check if the username already exists
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the user's password
    hashed_password = hash_password(user.password)

    # Create the new user
    return await crud.create_user(
        db,
        username=user.username,
        email=user.email,
        password=hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        is_verified=user.is_verified,
    )

@router.put("/users/{user_id}/", response_model=UserResponse)
async def update_user_api(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
):
    db_user = await crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Allow only the user themselves or superusers to update the user
    if db_user.id != current_user.id and not is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    # Update the user, including hashing the password if provided
    updated_user = await crud.update_user(db, user_id, user_update)
    return updated_user

@router.delete("/users/{user_id}/", response_model=dict)
async def delete_user_api(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(current_active_user),
):
    db_user = await crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Allow only the user themselves or superusers to delete the user
    if db_user.id != current_user.id and not is_superuser(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to delete this user")

    await crud.delete_user(db, user_id)
    return {"message": f"User with ID {user_id} has been deleted"}