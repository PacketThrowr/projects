from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.workout import Workout, WorkoutExercise, WorkoutSet
from app.schemas.workout import WorkoutCreate


async def create_workout(db: AsyncSession, workout: WorkoutCreate):
    db_workout = Workout(name=workout.name, description=workout.description)
    db.add(db_workout)
    await db.commit()
    await db.refresh(db_workout)

    for exercise in workout.exercises:
        db_workout_exercise = WorkoutExercise(
            workout_id=db_workout.id, exercise_name=exercise.exercise_name
        )
        db.add(db_workout_exercise)
        await db.commit()
        await db.refresh(db_workout_exercise)

        for set_data in exercise.sets:
            db_set = WorkoutSet(
                workout_exercise_id=db_workout_exercise.id,
                reps=set_data.reps,
                weight=set_data.weight,
                time=set_data.time,
                completed=set_data.completed,
            )
            db.add(db_set)
        await db.commit()
    return db_workout


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


async def update_workout_set(db: AsyncSession, set_id: int, updates: dict):
    result = await db.execute(select(WorkoutSet).where(WorkoutSet.id == set_id))
    db_set = result.scalars().first()
    if not db_set:
        return None
    for key, value in updates.items():
        setattr(db_set, key, value)
    await db.commit()
    await db.refresh(db_set)
    return db_set


async def delete_workout(db: AsyncSession, workout_id: int):
    result = await db.execute(select(Workout).where(Workout.id == workout_id))
    db_workout = result.scalars().first()
    if not db_workout:
        return None
    await db.delete(db_workout)
    await db.commit()
    return True


async def add_exercise_to_workout(db: AsyncSession, workout_id: int, exercise_name: str):
    # Validate workout existence
    result = await db.execute(select(Workout).where(Workout.id == workout_id))
    db_workout = result.scalars().first()
    if not db_workout:
        raise ValueError(f"Workout with ID {workout_id} does not exist")

    # Add exercise to workout
    db_workout_exercise = WorkoutExercise(
        workout_id=workout_id, exercise_name=exercise_name
    )
    db.add(db_workout_exercise)
    await db.commit()
    await db.refresh(db_workout_exercise)

    return db_workout_exercise
