from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.schemas.exercise import Exercise as ExerciseSchema, ExerciseCreate  # Pydantic schemas
from app import crud

router = APIRouter()

# Dependency to get DB session
async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

# GET all exercises
@router.get("/exercises/", response_model=list[ExerciseSchema])
async def read_exercises(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return crud.get_exercises(db, skip=skip, limit=limit)

# POST a new exercise
@router.post("/exercises/", response_model=ExerciseSchema)
async def create_exercise(exercise: ExerciseCreate, db: AsyncSession = Depends(get_db)):
    db_exercise = crud.get_exercise_by_name(db, name=exercise.name)
    if db_exercise:
        raise HTTPException(status_code=400, detail="Exercise already exists")
    return crud.create_exercise(db, exercise)

# PUT (update) an exercise
@router.put("/exercises/{exercise_id}/", response_model=ExerciseSchema)
async def update_exercise(exercise_id: int, updated_exercise: ExerciseCreate, db: AsyncSession = Depends(get_db)):
    db_exercise = crud.update_exercise(db, exercise_id, updated_exercise)
    if not db_exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return db_exercise

# DELETE an exercise
@router.delete("/exercises/{exercise_id}/", response_model=dict)
async def delete_exercise(exercise_id: int, db: AsyncSession = Depends(get_db)):
    success = crud.delete_exercise(db, exercise_id)
    if not success:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return {"message": f"Exercise with ID {exercise_id} has been deleted"}
