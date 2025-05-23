from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.schemas.profile import Profile, ProfileCreate, ProfileUpdate, WeightEntry, ProfileResponse, WeightEntryResponse
from app import crud
from app.auth.backend import current_active_user
from app.models.user import User

router = APIRouter()

# Dependency
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

@router.post("/profiles/", response_model=ProfileResponse)
async def create_profile(
    profile: ProfileCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    print(profile)
    return await crud.create_profile(db, profile, user_id=user.id)



@router.get("/profiles/", response_model=list[ProfileResponse])
async def read_profiles(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Fetch profiles using your CRUD function
    profiles = await crud.get_profiles_for_user(db, user_id=user.id)
    
    # Convert SQLAlchemy models to Pydantic models
    return [ProfileResponse.from_orm(profile) for profile in profiles]
    
@router.get("/profiles/{profile_id}/", response_model=ProfileResponse)
async def read_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Fetch the profile from the database
    db_profile = await crud.get_profile_by_id(db, profile_id)

    # Check if the profile exists and belongs to the current user
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Convert SQLAlchemy model to Pydantic response model
    return ProfileResponse.from_orm(db_profile)

@router.put("/profiles/{profile_id}/", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Fetch the profile
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        updated_profile = await crud.update_profile(db, profile_id, profile)
        return ProfileResponse.from_orm(updated_profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/profiles/{profile_id}/", response_model=dict)
async def delete_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    success = await crud.delete_profile(db, profile_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Profile with ID {profile_id} not found")
    
    return {"message": f"Profile with ID {profile_id} deleted"}

@router.get("/profiles/{profile_id}/weights/", response_model=list[WeightEntryResponse])
async def get_weights(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Fetch the profile
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        # Retrieve the weights
        weights = await crud.get_weights_for_profile(db, db_profile)
        return weights
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error retrieving weights")

@router.post("/profiles/{profile_id}/weights/", response_model=ProfileResponse)
async def add_weight(
    profile_id: int,
    weight: WeightEntry,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Fetch the profile
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        # Add the weight entry
        updated_profile = await crud.add_weight_to_profile(db, db_profile, weight)
        return ProfileResponse.from_orm(updated_profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/profiles/{profile_id}/weights/{date}/", response_model=ProfileResponse)
async def update_weight(
    profile_id: int,
    date: str,
    new_weight: WeightEntry,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Fetch the profile
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        # Update the weight entry
        updated_profile = await crud.update_weight_entry(db, db_profile, date, new_weight)
        return ProfileResponse.from_orm(updated_profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/profiles/{profile_id}/weights/{date}/", response_model=ProfileResponse)
async def delete_weight(
    profile_id: int,
    date: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Fetch the profile
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        # Delete the weight entry
        updated_profile = await crud.delete_weight_entry(db, db_profile, date)
        return ProfileResponse.from_orm(updated_profile)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))