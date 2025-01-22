from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.schemas.exercise import Exercise as ExerciseSchema, ExerciseCreate
from app import crud
from fastapi.logger import logger
import logging

router = APIRouter()
logger = logging.getLogger(__name__)
# Dependency for the database session
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

@router.get("/exercises/", response_model=list[ExerciseSchema])
async def get_all_exercises(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all exercises without pagination.
    """
    try:
        exercises = await crud.get_exercises(db)
        return exercises
    except Exception as e:
        logging.error(f"Failed to fetch exercises: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch exercises")

@router.post("/exercises/", response_model=ExerciseSchema)
async def create_new_exercise(exercise: ExerciseCreate, db: AsyncSession = Depends(get_db)):
    try:
        logger.info(f"Received exercise data: {exercise.dict()}")
        result = await crud.create_exercise(db, exercise)
        return result
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error creating exercise: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/exercises/{exercise_id}/", response_model=ExerciseSchema)
async def update_existing_exercise(exercise_id: int, updated_exercise: ExerciseCreate, db: AsyncSession = Depends(get_db)):
    updated = await crud.update_exercise(db, exercise_id, updated_exercise)
    if not updated:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return updated


@router.delete("/exercises/{exercise_id}/")
async def delete_exercise_route(exercise_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete an exercise by its ID.
    """
    try:
        return await crud.delete_exercise(db, exercise_id)
    except ValueError as e:
        logging.error(f"Error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete exercise")
