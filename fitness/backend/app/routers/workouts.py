from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.schemas.workout import (
    Workout as WorkoutSchema, 
    WorkoutCreate, 
    WorkoutSet as WorkoutSetSchema,
    SetType,
    SetUpdate,
    WeightSetUpdate,
    CardioSetUpdate,
    ExerciseAdd
)
from app.crud.workouts import (
    create_workout,
    get_workout,
    get_workouts,
    update_workout_set,
    delete_workout,
    add_exercise_to_workout,
)
from app.models.workout import (  # Import the models with different names
    WorkoutSet as WorkoutSetModel,
    WorkoutExercise,
    Workout as WorkoutModel
)
from app.auth.backend import current_active_user
from app.models.user import User
from app import crud
from app.utils import validate_user_profile
from app.crud.exercises import get_set_exercise_type
import logging
from sqlalchemy import select
logger = logging.getLogger(__name__)
router = APIRouter()


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


@router.get("/profiles/{profile_id}/workouts/", response_model=list[WorkoutSchema])
async def get_workouts_for_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Validate that the profile belongs to the current user
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")

    return await crud.get_workouts_for_profile(db, profile_id)


@router.post("/profiles/{profile_id}/workouts/", response_model=WorkoutSchema)
async def create_workout_for_profile(
    profile_id: int,
    workout: WorkoutCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await validate_user_profile(db, user, profile_id)
    workout.profile_id = profile_id
    return await crud.create_workout(db, workout)

@router.put("/profiles/{profile_id}/workouts/{workout_id}/", response_model=WorkoutSchema)
async def update_workout_route(
    profile_id: int,
    workout_id: int,
    workout_update: WorkoutCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Verify profile belongs to user
    await validate_user_profile(db, user, profile_id)
    
    try:
        updated_workout = await crud.update_workout(db, profile_id, workout_id, workout_update)
        if not updated_workout:
            raise HTTPException(status_code=404, detail="Workout not found")
        return updated_workout
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
@router.delete("/profiles/{profile_id}/workouts/{workout_id}/", response_model=dict)
async def delete_workout_route(
    profile_id: int,
    workout_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Verify the profile belongs to the user
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Delete the workout
    success = await delete_workout(db, profile_id, workout_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workout not found")
    return {"message": f"Workout with ID {workout_id} has been deleted"}


@router.put("/profiles/{profile_id}/workouts/{workout_id}/sets/{set_id}/", response_model=WorkoutSetSchema)
async def update_workout_set_route(
    profile_id: int,
    workout_id: int,  # Added workout_id parameter
    set_id: int,
    set_data: WeightSetUpdate | CardioSetUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    logger.info(f"Updating set {set_id} for profile {profile_id} in workout {workout_id}")

    # Verify the profile belongs to the user
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        # Update the workout set
        db_set = await update_workout_set(
            db, 
            profile_id,
            workout_id,  # Pass workout_id to crud function
            set_id, 
            set_data.model_dump(exclude_unset=True)
        )
        if not db_set:
            raise HTTPException(status_code=404, detail="Set not found")
        return db_set
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/profiles/{profile_id}/workouts/{workout_id}/exercises/", response_model=dict)
async def add_exercise_route(
    profile_id: int,
    workout_id: int,
    exercise_data: ExerciseAdd,  # Change to use the Pydantic model
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Verify the profile belongs to the user
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Add the exercise to the workout
    try:
        workout_exercise = await add_exercise_to_workout(
            db, 
            profile_id, 
            workout_id, 
            exercise_data.exercise_name
        )
        return {"message": f"Exercise '{exercise_data.exercise_name}' added to Workout {workout_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/profiles/{profile_id}/workouts/{workout_id}/exercises/{exercise_id}/sets", response_model=WorkoutSetSchema)
async def add_set_to_exercise_route(
    profile_id: int,
    workout_id: int,
    exercise_id: int,
    set_data: WeightSetUpdate | CardioSetUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Verify the profile belongs to the user
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")

    try:
        new_set = await crud.add_set_to_exercise(
            db, 
            profile_id, 
            workout_id, 
            exercise_id, 
            set_data.model_dump(exclude_unset=True)
        )
        return new_set
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))