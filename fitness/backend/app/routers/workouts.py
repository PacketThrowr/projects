from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.schemas.workout import Workout, WorkoutCreate, WorkoutSet
from app.crud.workouts import (
    create_workout,
    get_workout,
    get_workouts,
    update_workout_set,
    delete_workout,
    add_exercise_to_workout,
)

router = APIRouter()


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


@router.post("/workouts/", response_model=Workout)
async def create_workout_route(workout: WorkoutCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await create_workout(db, workout)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/workouts/{workout_id}/", response_model=Workout)
async def read_workout(workout_id: int, db: AsyncSession = Depends(get_db)):
    db_workout = await get_workout(db, workout_id)
    if not db_workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return db_workout


@router.get("/workouts/", response_model=list[Workout])
async def read_workouts(db: AsyncSession = Depends(get_db)):
    return await get_workouts(db)


@router.put("/workouts/sets/{set_id}/", response_model=WorkoutSet)
async def update_workout_set_route(set_id: int, updates: dict, db: AsyncSession = Depends(get_db)):
    db_set = await update_workout_set(db, set_id, updates)
    if not db_set:
        raise HTTPException(status_code=404, detail="Set not found")
    return db_set


@router.delete("/workouts/{workout_id}/", response_model=dict)
async def delete_workout_route(workout_id: int, db: AsyncSession = Depends(get_db)):
    success = await delete_workout(db, workout_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"message": f"Workout with ID {workout_id} has been deleted"}


@router.post("/workouts/{workout_id}/exercises/", response_model=dict)
async def add_exercise_route(workout_id: int, exercise_name: str, db: AsyncSession = Depends(get_db)):
    try:
        workout_exercise = await add_exercise_to_workout(db, workout_id, exercise_name)
        return {"message": f"Exercise '{exercise_name}' added to Workout {workout_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
