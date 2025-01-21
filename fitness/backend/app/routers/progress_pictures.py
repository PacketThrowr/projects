from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.database import async_session_maker
from app.schemas.progress_picture import ProgressPicture
from app.crud.progress_pictures import (
    add_progress_picture,
    get_progress_pictures,
    delete_progress_picture,
)
from app.crud.profiles import get_profile_by_id
from app.auth.backend import current_active_user
from app.models.user import User

router = APIRouter()

# Dependency
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def validate_user_profile_association(
    db: AsyncSession, profile_id: int, user: User
):
    profile = await get_profile_by_id(db, profile_id)
    if not profile or profile.user_id != user.id:
        raise HTTPException(
            status_code=403, detail="You are not authorized to access this profile"
        )
    return profile


@router.post("/profiles/{profile_id}/progress-pictures/", response_model=ProgressPicture)
async def upload_progress_picture(
    profile_id: int,
    picture: UploadFile = File(...),
    weight: float = 0.0,
    date: date = date.today(),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await validate_user_profile_association(db, profile_id, user)

    try:
        # Save the uploaded image to a directory
        file_location = f"media/progress_pictures/{profile_id}_{date}_{picture.filename}"
        with open(file_location, "wb") as f:
            f.write(await picture.read())

        # Add the progress picture to the database
        return await add_progress_picture(db, profile_id, date, weight, file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{profile_id}/progress-pictures/", response_model=list[ProgressPicture])
async def fetch_progress_pictures(
    profile_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)
):
    await validate_user_profile_association(db, profile_id, user)

    pictures = await get_progress_pictures(db, profile_id)
    if not pictures:
        raise HTTPException(status_code=404, detail="No progress pictures found")
    return pictures


@router.delete("/progress-pictures/{picture_id}/", response_model=dict)
async def remove_progress_picture(
    profile_id: int,
    picture_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    profile = await validate_user_profile_association(db, profile_id, user)

    # Ensure the picture belongs to the profile
    pictures = await get_progress_pictures(db, profile.id)
    if not any(picture.id == picture_id for picture in pictures):
        raise HTTPException(
            status_code=403, detail="You are not authorized to delete this picture"
        )

    deleted_picture = await delete_progress_picture(db, picture_id)
    if not deleted_picture:
        raise HTTPException(status_code=404, detail="Progress picture not found")
    return {"message": f"Progress picture with ID {picture_id} has been deleted"}
