from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.database import async_session_maker
from app.schemas.progress_picture import ProgressPicture, ProgressPictureCreate
from app import crud

router = APIRouter()

# Dependency
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


@router.post("/profiles/{profile_id}/progress-pictures/", response_model=ProgressPicture)
async def upload_progress_picture(
    profile_id: int,
    picture: UploadFile = File(...),
    weight: float = 0.0,
    date: date = date.today(),
    db: AsyncSession = Depends(get_db),
):
    try:
        # Save the uploaded image to a directory
        file_location = f"media/progress_pictures/{profile_id}_{date}_{picture.filename}"
        with open(file_location, "wb") as f:
            f.write(await picture.read())

        # Add the progress picture to the database
        return crud.add_progress_picture(db, profile_id, date, weight, file_location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profiles/{profile_id}/progress-pictures/", response_model=list[ProgressPicture])
async def get_progress_pictures(profile_id: int, db: AsyncSession = Depends(get_db)):
    pictures = crud.get_progress_pictures(db, profile_id)
    if not pictures:
        raise HTTPException(status_code=404, detail="No progress pictures found")
    return pictures


@router.delete("/progress-pictures/{picture_id}/", response_model=dict)
async def delete_progress_picture(picture_id: int, db: AsyncSession = Depends(get_db)):
    deleted_picture = crud.delete_progress_picture(db, picture_id)
    if not deleted_picture:
        raise HTTPException(status_code=404, detail="Progress picture not found")
    return {"message": f"Progress picture with ID {picture_id} has been deleted"}
