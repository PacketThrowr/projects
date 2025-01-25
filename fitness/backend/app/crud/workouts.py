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
from datetime import datetime

async def create_workout(db: AsyncSession, workout: WorkoutCreate):
    # Validate profile existence
    result = await db.execute(select(Profile).where(Profile.id == workout.profile_id))
    db_profile = result.scalars().first()
    if not db_profile:
        raise ValueError(f"Profile with ID {workout.profile_id} does not exist")
    current_datetime = datetime.now()
    current_time_str = current_datetime.time().strftime("%H:%M:%S")
    # Create the workout
    db_workout = Workout(
        name=workout.name,
        description=workout.description,
        profile_id=workout.profile_id,
        date=datetime.now().strftime("%Y-%m-%d"),
        start_time=current_time_str,
        end_time=workout.end_time
    )
    db.add(db_workout)
    await db.commit()
    await db.refresh(db_workout)

    return await get_workout(db, db_workout.id)  # Fetch and return the full workout with exercises and sets


async def get_workouts_for_profile(db: AsyncSession, profile_id: int):
    result = await db.execute(
        select(Workout)
        .where(Workout.profile_id == profile_id)
        .options(selectinload(Workout.exercises).selectinload(WorkoutExercise.sets))
    )
    return result.scalars().all()

async def get_workout(db: AsyncSession, workout_id: int):
    result = await db.execute(
        select(Workout)
        .where(Workout.id == workout_id)
        .options(selectinload(Workout.exercises).selectinload(WorkoutExercise.sets))
    )
    return result.scalars().first()


async def get_workouts(db: AsyncSession):
    result = await db.execute(
        select(Workout).options(
            selectinload(Workout.exercises).selectinload(WorkoutExercise.sets)
        )
    )
    return result.scalars().all()


async def update_workout_set(db: AsyncSession, profile_id: int, workout_id: int, exercise_id: int, set_id: int, updates: dict):
    stmt = (
        select(WorkoutSet, Exercise.type.label('exercise_type'))
        .select_from(WorkoutSet)
        .join(WorkoutExercise, WorkoutSet.exercise_id == WorkoutExercise.id)
        .join(Workout, WorkoutExercise.workout_id == Workout.id)
        .join(Exercise, WorkoutExercise.exercise_id == Exercise.id)
        .where(
            Workout.profile_id == profile_id,
            Workout.id == workout_id,
            WorkoutExercise.id == exercise_id,
            WorkoutSet.id == set_id
        )
    )
    result = await db.execute(stmt)
    row = result.first()
    
    if not row:
        return None
        
    db_set, exercise_type = row

    # Validate updates match exercise type
    if exercise_type == "CARDIO" and ('weight' in updates or 'reps' in updates):
        raise ValueError("Cannot update weight/reps for a cardio exercise")
    if exercise_type == "WEIGHTS" and 'time' in updates:
        raise ValueError("Cannot update time for a weight exercise")

    # Update only valid fields
    for key, value in updates.items():
        if hasattr(db_set, key):
            setattr(db_set, key, value)

    await db.commit()
    await db.refresh(db_set)
    return db_set


async def delete_workout(db: AsyncSession, profile_id: int, workout_id: int):
    stmt = select(Workout).where(
        Workout.id == workout_id, Workout.profile_id == profile_id
    )
    result = await db.execute(stmt)
    db_workout = result.scalars().first()

    if not db_workout:
        return None

    await db.delete(db_workout)
    await db.commit()
    return True


async def add_exercise_to_workout(db: AsyncSession, profile_id: int, workout_id: int, exercise_name: str):
    # First verify the workout exists and belongs to the profile
    stmt = select(Workout).where(
        Workout.id == workout_id, Workout.profile_id == profile_id
    )
    result = await db.execute(stmt)
    db_workout = result.scalars().first()

    if not db_workout:
        raise ValueError(f"Workout with ID {workout_id} does not exist for the given profile")

    # Look up the exercise by name
    exercise_stmt = select(Exercise).where(Exercise.name == exercise_name)
    result = await db.execute(exercise_stmt)
    db_exercise = result.scalars().first()

    if not db_exercise:
        raise ValueError(f"Exercise with name '{exercise_name}' not found")

    # Add exercise to workout using exercise_id
    db_workout_exercise = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=db_exercise.id  # Use exercise_id instead of exercise_name
    )
    db.add(db_workout_exercise)
    await db.commit()
    await db.refresh(db_workout_exercise)

    return db_workout_exercise

async def add_set_to_exercise(
    db: AsyncSession,
    profile_id: int,
    workout_id: int,
    exercise_id: int,
    set_data: dict,
) -> WorkoutSet:
    """
    Add a new set to a workout exercise.
    Validates that the workout and exercise belong to the correct profile.
    """
    # Verify the workout exercise exists and belongs to this profile
    result = await db.execute(
        select(WorkoutExercise)
        .join(Workout)
        .where(
            WorkoutExercise.id == exercise_id,
            Workout.id == workout_id,
            Workout.profile_id == profile_id,
        )
    )
    db_workout_exercise = result.scalars().first()

    if not db_workout_exercise:
        raise ValueError("Exercise not found in workout")

    # Validate that either 'reps' or 'time' is provided in `set_data`
    reps = set_data.get("reps")
    time = set_data.get("time")

    if reps is None and time is None:
        raise ValueError("Either 'reps' or 'time' must be provided (not both null).")

    # Create the new set
    new_set = WorkoutSet(
        exercise_id=db_workout_exercise.id,
        reps=reps if reps is not None else 0,
        time=time if time is not None else 0.0,
        weight=set_data.get("weight", 0.0),
        completed=set_data.get("completed", False),
    )

    db.add(new_set)
    await db.commit()
    await db.refresh(new_set)

    return new_set

async def update_workout(
    db: AsyncSession, 
    profile_id: int, 
    workout_id: int, 
    workout_data: WorkoutCreate
) -> Optional[Workout]:
    # Verify the workout exists and belongs to the profile
    stmt = select(Workout).where(
        Workout.id == workout_id,
        Workout.profile_id == profile_id
    )
    result = await db.execute(stmt)
    db_workout = result.scalars().first()

    if not db_workout:
        return None

    # Update basic workout fields
    db_workout.name = workout_data.name
    db_workout.description = workout_data.description

    # Handle exercises updates if provided
    if workout_data.exercises:
        # Remove existing exercises (and their sets due to cascade)
        await db.execute(
            delete(WorkoutExercise).where(WorkoutExercise.workout_id == workout_id)
        )
        
        # Add new exercises
        for exercise in workout_data.exercises:
            db_workout_exercise = WorkoutExercise(
                workout_id=workout_id,
                exercise_id=exercise.exercise_id,
            )
            db.add(db_workout_exercise)
            await db.commit()
            await db.refresh(db_workout_exercise)

            # Add sets for this exercise if provided
            for set_data in exercise.sets:
                db_set = WorkoutSet(
                    exercise_id=db_workout_exercise.id,
                    reps=set_data.reps,
                    weight=set_data.weight,
                    time=set_data.time,
                    completed=set_data.completed,
                )
                db.add(db_set)

    await db.commit()
    await db.refresh(db_workout)
    
    # Return the full workout with its relationships loaded
    return await get_workout(db, workout_id)

async def delete_workout_exercise(db: AsyncSession, profile_id: int, workout_id: int, exercise_id: int):
    stmt = (
        delete(WorkoutExercise)
        .where(
            WorkoutExercise.id == exercise_id,
            WorkoutExercise.workout_id == workout_id,
            exists().where(
                Workout.id == workout_id,
                Workout.profile_id == profile_id
            )
        )
        .returning(WorkoutExercise.id)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

async def get_exercise_sets(db: AsyncSession, profile_id: int, workout_id: int, exercise_id: int):
    stmt = (
        select(WorkoutSet)
        .join(WorkoutExercise)
        .join(Workout)
        .where(
            Workout.profile_id == profile_id,
            Workout.id == workout_id,
            WorkoutExercise.id == exercise_id
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

async def delete_exercise_set(db: AsyncSession, profile_id: int, workout_id: int, exercise_id: int, set_id: int):
    stmt = (
        delete(WorkoutSet)
        .where(
            WorkoutSet.id == set_id,
            WorkoutSet.exercise_id == exercise_id,
            exists().where(
                WorkoutExercise.id == exercise_id,
                WorkoutExercise.workout_id == workout_id,
                Workout.id == workout_id,
                Workout.profile_id == profile_id
            )
        )
        .returning(WorkoutSet.id)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()

async def get_workout_exercises(db: AsyncSession, profile_id: int, workout_id: int):
    stmt = (
        select(WorkoutExercise)
        .join(Workout)
        .options(selectinload(WorkoutExercise.sets))
        .where(
            Workout.profile_id == profile_id,
            Workout.id == workout_id
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()