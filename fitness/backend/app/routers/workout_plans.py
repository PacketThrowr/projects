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
    WorkoutPlan,
    WorkoutPlanExercise,
    WorkoutPlanSet,
    WorkoutPlanCreate
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