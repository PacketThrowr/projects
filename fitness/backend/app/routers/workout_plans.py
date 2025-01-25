from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import async_session_maker
from app.schemas.exercise import ExerciseSchema
from app.schemas.workout import (
    Workout as WorkoutSchema, 
    WorkoutCreate, 
    WorkoutSet as WorkoutSetSchema,
    SetType,
    SetUpdate,
    WeightSetUpdate,
    CardioSetUpdate,
    ExerciseAdd,
    WorkoutExerciseSchema
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
from app.schemas.workout_plan import (
    WorkoutPlanExercise as WorkoutPlanExerciseSchema,
    WorkoutPlanSet as WorkoutPlanSetSchema,
    ExerciseAdd,
    WeightSetUpdate,
    CardioSetUpdate,
    WorkoutPlan,
    WorkoutPlanCreate
)
from app.auth.backend import current_active_user
from app.models.user import User
from app import crud
from app.utils import validate_user_profile
import logging
from sqlalchemy import select
from app.crud.workout_plans import (
    add_exercise_to_workout_plan,
    add_set_to_workout_plan_exercise,
    get_workout_plan_exercises,
    get_exercise_sets_in_workout_plan,
    update_set_in_workout_plan,
    delete_exercise_from_workout_plan,
    delete_set_from_workout_plan,
)
logger = logging.getLogger(__name__)
router = APIRouter()

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

@router.get("/profiles/{profile_id}/workout_plans/", response_model=list[WorkoutPlan])
async def get_workout_plans_for_profile(
    profile_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(current_active_user)
):
    await validate_user_profile(db, user, profile_id)
    return await crud.get_workout_plans_for_profile(db, profile_id)


@router.post("/profiles/{profile_id}/workout_plans/", response_model=WorkoutPlan)
async def create_workout_plan_for_profile(
    profile_id: int,
    workout_plan: WorkoutPlanCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Validate the user's profile ownership
    await validate_user_profile(db, user, profile_id)

    # Set the profile ID for the workout plan
    workout_plan.profile_id = profile_id

    # Call the correct CRUD function
    created_plan = await crud.create_workout_plan_for_profile(db, profile_id, workout_plan)

    # Return the SQLAlchemy instance converted to a Pydantic model
    return created_plan



@router.delete("/profiles/{profile_id}/workout_plans/{workout_plan_id}/", response_model=dict)
async def delete_workout_plan_route(
    profile_id: int,
    workout_plan_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await validate_user_profile(db, user, profile_id)
    success = await crud.delete_workout_plan(db, profile_id, workout_plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workout plan not found")
    return {"message": f"Workout plan with ID {workout_plan_id} has been deleted"}

@router.get("/profiles/{profile_id}/workout_plans/{workout_plan_id}/exercises/", response_model=list[WorkoutPlanExerciseSchema])
async def get_workout_plan_exercises_route(
    profile_id: int,
    workout_plan_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await validate_user_profile(db, user, profile_id)
    return await get_workout_plan_exercises(db, profile_id, workout_plan_id)

@router.post("/profiles/{profile_id}/workout_plans/{workout_plan_id}/exercises/", response_model=WorkoutPlanExerciseSchema)
async def add_exercise_to_workout_plan_route(
    profile_id: int,
    workout_plan_id: int,
    exercise_data: ExerciseAdd,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await validate_user_profile(db, user, profile_id)
    try:
        exercise = await add_exercise_to_workout_plan(
            db, profile_id, workout_plan_id, exercise_data.exercise_id
        )
        return exercise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/profiles/{profile_id}/workout_plans/{workout_plan_id}/exercises/{exercise_id}/", response_model=dict)
async def delete_exercise_from_workout_plan_route(
    profile_id: int,
    workout_plan_id: int,
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await validate_user_profile(db, user, profile_id)
    success = await delete_exercise_from_workout_plan(
        db, profile_id, workout_plan_id, exercise_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return {"message": f"Exercise {exercise_id} deleted from Workout Plan {workout_plan_id}"}

@router.get("/profiles/{profile_id}/workout_plans/{workout_plan_id}/exercises/{exercise_id}/sets/", response_model=list[WorkoutPlanSetSchema])
async def get_exercise_sets_in_workout_plan_route(
    profile_id: int,
    workout_plan_id: int,
    exercise_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await validate_user_profile(db, user, profile_id)
    return await get_exercise_sets_in_workout_plan(db, profile_id, workout_plan_id, exercise_id)

@router.post("/profiles/{profile_id}/workout_plans/{workout_plan_id}/exercises/{exercise_id}/sets/", response_model=WorkoutPlanSetSchema)
async def add_set_to_workout_plan_exercise_route(
    profile_id: int,
    workout_plan_id: int,
    exercise_id: int,
    set_data: WeightSetUpdate | CardioSetUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await validate_user_profile(db, user, profile_id)
    try:
        new_set = await add_set_to_workout_plan_exercise(
            db,
            profile_id,
            workout_plan_id,
            exercise_id,
            set_data.model_dump(exclude_unset=True),
        )
        return new_set
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/profiles/{profile_id}/workout_plans/{workout_plan_id}/exercises/{exercise_id}/sets/{set_id}/", response_model=WorkoutPlanSetSchema)
async def update_set_in_workout_plan_route(
    profile_id: int,
    workout_plan_id: int,
    exercise_id: int,
    set_id: int,
    set_data: WeightSetUpdate | CardioSetUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await validate_user_profile(db, user, profile_id)
    try:
        updated_set = await update_set_in_workout_plan(
            db,
            profile_id,
            workout_plan_id,
            exercise_id,
            set_id,
            set_data.model_dump(exclude_unset=True),
        )
        if not updated_set:
            raise HTTPException(status_code=404, detail="Set not found")
        return updated_set
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/profiles/{profile_id}/workout_plans/{workout_plan_id}/exercises/{exercise_id}/sets/{set_id}/", response_model=dict)
async def delete_set_from_workout_plan_route(
    profile_id: int,
    workout_plan_id: int,
    exercise_id: int,
    set_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    await validate_user_profile(db, user, profile_id)
    success = await delete_set_from_workout_plan(
        db, profile_id, workout_plan_id, exercise_id, set_id
    )
    if not success:
        raise HTTPException(status_code=404, detail="Set not found")
    return {"message": f"Set {set_id} deleted from Workout Plan {workout_plan_id}"}

@router.put("/profiles/{profile_id}/workout_plans/{workout_plan_id}/", response_model=WorkoutPlan)
async def update_workout_plan_for_profile_endpoint(
    profile_id: int,
    workout_plan_id: int,
    workout_plan_update: WorkoutPlanCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    # Validate profile ownership
    await validate_user_profile(db, user, profile_id)

    # Ensure the workout plan exists and belongs to the profile
    existing_plan = await crud.get_workout_plan(db, profile_id, workout_plan_id)
    if not existing_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found")

    # Update the workout plan
    updated_plan = await crud.update_workout_plan_for_profile(
        db, workout_plan_id, workout_plan_update
    )

    return updated_plan