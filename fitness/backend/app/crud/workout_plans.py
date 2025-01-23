from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.workout import Workout, WorkoutExercise, WorkoutSet
from app.schemas.workout import WorkoutCreate
from sqlalchemy.orm import joinedload, selectinload
from app.schemas.profile import Profile, ProfileCreate, ProfileUpdate, WeightEntry, ProfileResponse, WeightEntryResponse
from app.models.exercise import Exercise
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.profile import Profile  # Ensure this is the SQLAlchemy model
from typing import Optional
from sqlalchemy import delete, exists
from app.models.workout_plan import WorkoutPlan, WorkoutPlanExercise, WorkoutPlanSet  # Ensure WorkoutPlan is imported
from app.schemas.workout_plan import WorkoutPlan as WorkoutPlanSchema
from app.schemas.workout_plan import WorkoutPlanCreate

async def create_workout_plan(db: AsyncSession, workout_plan: WorkoutPlanCreate):
    # Create a new WorkoutPlan instance using the SQLAlchemy model
    db_workout_plan = WorkoutPlan(
        name=workout_plan.name,
        description=workout_plan.description,
        profile_id=workout_plan.profile_id
    )
    db.add(db_workout_plan)
    await db.commit()
    await db.refresh(db_workout_plan)  # Refresh to get the generated ID
    return db_workout_plan


import logging

logger = logging.getLogger(__name__)

async def create_workout_plan_for_profile(db: AsyncSession, profile_id: int, workout_plan_data: WorkoutPlanCreate):
    # Create the workout plan
    created_plan = await create_workout_plan(db, workout_plan_data)

    # Add exercises to the workout plan
    for exercise_data in workout_plan_data.exercises:
        db_exercise = WorkoutPlanExercise(
            workout_plan_id=created_plan.id,
            exercise_id=exercise_data.exercise_id
        )
        db.add(db_exercise)
        await db.flush()  # Ensure the exercise gets an ID before adding sets

        # Add sets to the exercise
        for set_data in exercise_data.sets:
            db_set = WorkoutPlanSet(
                exercise_id=db_exercise.id,
                reps=set_data.reps,
                weight=set_data.weight,
                time=set_data.time,
                completed=set_data.completed
            )
            db.add(db_set)

    # Commit all changes
    await db.commit()

    # Reload the workout plan with its relationships eagerly loaded
    result = await db.execute(
        select(WorkoutPlan)
        .options(
            selectinload(WorkoutPlan.exercises).selectinload(WorkoutPlanExercise.sets)
        )
        .where(WorkoutPlan.id == created_plan.id)
    )

    fully_loaded_plan = result.scalars().first()

    # Use the Pydantic schema to serialize the SQLAlchemy object
    return WorkoutPlanSchema.from_orm(fully_loaded_plan)



async def get_workout_plans_for_profile(db: AsyncSession, profile_id: int):
    result = await db.execute(
        select(WorkoutPlan).where(WorkoutPlan.profile_id == profile_id)
    )
    return result.scalars().all()

async def get_workout_plan(db: AsyncSession, profile_id: int, workout_plan_id: int):
    result = await db.execute(
        select(WorkoutPlan).where(
            WorkoutPlan.profile_id == profile_id, WorkoutPlan.id == workout_plan_id
        )
    )
    return result.scalars().first()


async def delete_workout_plan(db: AsyncSession, profile_id: int, workout_plan_id: int):
    result = await db.execute(
        select(WorkoutPlan).where(
            WorkoutPlan.profile_id == profile_id, WorkoutPlan.id == workout_plan_id
        )
    )
    workout_plan = result.scalars().first()
    if workout_plan:
        await db.delete(workout_plan)
        await db.commit()
        return True
    return False