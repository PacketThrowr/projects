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
        select(WorkoutPlan)
        .options(
            selectinload(WorkoutPlan.exercises).selectinload(WorkoutPlanExercise.exercise),  # Ensure Exercise is loaded
            selectinload(WorkoutPlan.exercises).selectinload(WorkoutPlanExercise.sets)
        )
        .where(WorkoutPlan.profile_id == profile_id)
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

async def add_exercise_to_workout_plan(
    db: AsyncSession, profile_id: int, workout_plan_id: int, exercise_id: int
):
    # Ensure the workout plan exists
    result = await db.execute(
        select(WorkoutPlan)
        .where(
            WorkoutPlan.id == workout_plan_id,
            WorkoutPlan.profile_id == profile_id
        )
    )
    plan = result.scalars().first()
    if not plan:
        raise ValueError("Plan not found")

    # Add exercise
    exercise = WorkoutPlanExercise(
        workout_plan_id=workout_plan_id,
        exercise_id=exercise_id
    )
    db.add(exercise)
    await db.commit()

    # Load relationships
    result = await db.execute(
        select(WorkoutPlanExercise)
        .options(
            selectinload(WorkoutPlanExercise.exercise),
            selectinload(WorkoutPlanExercise.sets)
        )
        .where(WorkoutPlanExercise.id == exercise.id)
    )
    exercise = result.scalars().first()

    # Manual response
    return {
        "id": exercise.id,
        "workout_plan_id": exercise.workout_plan_id,
        "exercise_id": exercise.exercise_id,
        "exercise": {
            "id": exercise.exercise.id,
            "name": exercise.exercise.name,
            "description": exercise.exercise.description,
            "weight_type": exercise.exercise.weight_type
        },
        "sets": []
    }

async def add_set_to_workout_plan_exercise(
    db: AsyncSession, profile_id: int, workout_plan_id: int, exercise_id: int, set_data: dict
):
    # Ensure the exercise exists within the specified workout plan and profile
    stmt = (
        select(WorkoutPlanExercise)
        .join(WorkoutPlan)
        .where(
            WorkoutPlanExercise.id == exercise_id,
            WorkoutPlan.id == workout_plan_id,
            WorkoutPlan.profile_id == profile_id
        )
    )
    result = await db.execute(stmt)
    db_exercise = result.scalars().first()

    if not db_exercise:
        raise ValueError("Exercise not found in the specified workout plan")

    # Add the set to the exercise
    db_set = WorkoutPlanSet(
        exercise_id=exercise_id,
        reps=set_data.get("reps"),
        weight=set_data.get("weight"),
        time=set_data.get("time"),
        completed=set_data.get("completed", False),
    )
    db.add(db_set)
    await db.commit()
    await db.refresh(db_set)
    return db_set

async def get_workout_plan_exercises(db: AsyncSession, profile_id: int, workout_plan_id: int):
    stmt = (
        select(WorkoutPlanExercise)
        .join(WorkoutPlan)
        .options(
            selectinload(WorkoutPlanExercise.exercise),
            selectinload(WorkoutPlanExercise.sets)
        )
        .where(
            WorkoutPlan.id == workout_plan_id,
            WorkoutPlan.profile_id == profile_id
        )
    )
    result = await db.execute(stmt)
    exercises = result.scalars().all()

    return [{
        "id": exercise.id,
        "workout_plan_id": exercise.workout_plan_id,
        "exercise_id": exercise.exercise_id,
        "exercise": {
            "id": exercise.exercise.id,
            "name": exercise.exercise.name,
            "description": exercise.exercise.description,
            "weight_type": exercise.exercise.weight_type
        },
        "sets": [{
            "id": set.id,
            "reps": set.reps,
            "weight": set.weight,
            "time": set.time,
            "completed": set.completed,
            "exercise_id": set.exercise_id
        } for set in exercise.sets]
    } for exercise in exercises]

async def get_exercise_sets_in_workout_plan(
    db: AsyncSession, profile_id: int, workout_plan_id: int, exercise_id: int
):
    stmt = (
        select(WorkoutPlanSet)
        .join(WorkoutPlanExercise)
        .join(WorkoutPlan)
        .where(
            WorkoutPlan.profile_id == profile_id,
            WorkoutPlan.id == workout_plan_id,
            WorkoutPlanExercise.id == exercise_id
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def update_set_in_workout_plan(
    db: AsyncSession, profile_id: int, workout_plan_id: int, exercise_id: int, set_id: int, updates: dict
):
    stmt = (
        select(WorkoutPlanSet)
        .join(WorkoutPlanExercise)
        .join(WorkoutPlan)
        .where(
            WorkoutPlanSet.id == set_id,
            WorkoutPlanExercise.id == exercise_id,
            WorkoutPlan.id == workout_plan_id,
            WorkoutPlan.profile_id == profile_id
        )
    )
    result = await db.execute(stmt)
    db_set = result.scalars().first()

    if not db_set:
        raise ValueError("Set not found in the workout plan")

    # Update the fields
    for key, value in updates.items():
        if hasattr(db_set, key):
            setattr(db_set, key, value)

    await db.commit()
    await db.refresh(db_set)
    return db_set

async def delete_exercise_from_workout_plan(
    db: AsyncSession, profile_id: int, workout_plan_id: int, exercise_id: int
):
    stmt = (
        select(WorkoutPlanExercise)
        .join(WorkoutPlan)
        .where(
            WorkoutPlanExercise.id == exercise_id,
            WorkoutPlan.id == workout_plan_id,
            WorkoutPlan.profile_id == profile_id
        )
    )
    result = await db.execute(stmt)
    db_exercise = result.scalars().first()

    if not db_exercise:
        raise ValueError("Exercise not found in the workout plan")

    await db.delete(db_exercise)
    await db.commit()
    return True

async def delete_set_from_workout_plan(
    db: AsyncSession, profile_id: int, workout_plan_id: int, exercise_id: int, set_id: int
):
    stmt = (
        select(WorkoutPlanSet)
        .join(WorkoutPlanExercise)
        .join(WorkoutPlan)
        .where(
            WorkoutPlanSet.id == set_id,
            WorkoutPlanExercise.id == exercise_id,
            WorkoutPlan.id == workout_plan_id,
            WorkoutPlan.profile_id == profile_id
        )
    )
    result = await db.execute(stmt)
    db_set = result.scalars().first()

    if not db_set:
        raise ValueError("Set not found in the workout plan")

    await db.delete(db_set)
    await db.commit()
    return True

async def update_workout_plan_for_profile(db: AsyncSession, workout_plan_id: int, workout_plan_data: WorkoutPlanCreate):
    # Previous code remains the same until commit()
    await db.commit()

    # Load updated workout plan with relationships
    result = await db.execute(
        select(WorkoutPlan)
        .options(
            selectinload(WorkoutPlan.exercises).selectinload(WorkoutPlanExercise.exercise),
            selectinload(WorkoutPlan.exercises).selectinload(WorkoutPlanExercise.sets)
        )
        .where(WorkoutPlan.id == workout_plan_id)
    )
    plan = result.scalars().first()

    # Manually construct response
    return {
        "id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "profile_id": plan.profile_id,
        "exercises": [{
            "id": exercise.id,
            "exercise_id": exercise.exercise_id,
            "workout_plan_id": exercise.workout_plan_id,  # Add this line
            "exercise": {
                "id": exercise.exercise.id,
                "name": exercise.exercise.name,
                "description": exercise.exercise.description,
                "weight_type": exercise.exercise.weight_type
            },
            "sets": [{
                "id": set.id,
                "reps": set.reps,
                "weight": set.weight,
                "time": set.time,
                "completed": set.completed,
                "exercise_id": set.exercise_id
            } for set in exercise.sets]
        } for exercise in plan.exercises]
    }