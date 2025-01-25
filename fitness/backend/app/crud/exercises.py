from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseCreate
from app.schemas.exercise import Exercise as ExerciseSchema
from app.models.workout import WorkoutSet, WorkoutExercise
import logging
logger = logging.getLogger(__name__)
async def get_exercises(db: AsyncSession):
    """
    Retrieve all exercises from the database.
    """
    try:
        stmt = select(Exercise)  # Select all exercises
        result = await db.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        logging.error(f"Error fetching exercises: {str(e)}")
        raise


# Get an exercise by name
async def get_exercise_by_name(db: AsyncSession, name: str):
    stmt = select(Exercise).where(Exercise.name == name)
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_exercise(db: AsyncSession, exercise: ExerciseCreate):
    try:
        db_exercise = Exercise(
            name=exercise.name,
            picture=exercise.picture,
            force=exercise.force,  # New field
            level=exercise.level,  # New field
            mechanic=exercise.mechanic,  # New field
            equipment=exercise.equipment,  # New field
            primaryMuscles=exercise.primaryMuscles,  # New field
            secondaryMuscles=exercise.secondaryMuscles,  # New field
            instructions=exercise.instructions,  # New field
            category=exercise.category,
            recorded_type=exercise.recorded_type  # New field
        )
        db.add(db_exercise)
        await db.commit()
        await db.refresh(db_exercise)
        return db_exercise
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Error creating exercise: {str(e)}")



async def update_exercise(db: AsyncSession, exercise_id: int, updated_exercise: ExerciseCreate):
    stmt = select(Exercise).where(Exercise.id == exercise_id)
    result = await db.execute(stmt)
    db_exercise = result.scalars().first()
    
    if not db_exercise:
        return None

    # Update the exercise with the new values
    for field, value in updated_exercise.model_dump(exclude_unset=True).items():
        if field in ['type', 'weight_type', 'measurement_type'] and value is not None:
            value = value.value  # Extract enum value
        setattr(db_exercise, field, value)
    
    try:
        await db.commit()
        await db.refresh(db_exercise)
        return db_exercise
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Database error occurred: {str(e)}")

# Delete an exercise
async def delete_exercise(db: AsyncSession, exercise_id: int):
    """
    Delete an exercise by its ID.
    """
    try:
        # Fetch the exercise by ID
        stmt = select(Exercise).where(Exercise.id == exercise_id)
        result = await db.execute(stmt)
        exercise = result.scalars().first()

        # If exercise not found, raise an error
        if not exercise:
            raise ValueError("Exercise not found")

        # Delete the exercise
        await db.delete(exercise)
        await db.commit()
        return {"message": "Exercise deleted successfully"}
    except Exception as e:
        logging.error(f"Error deleting exercise: {str(e)}")
        raise

'''
async def get_set_exercise_category(db: AsyncSession, set_id: int):
    """Get the exercise category for a given set"""
    stmt = (
        select(Exercise.category)  # Fetch the category instead of type
        .select_from(WorkoutSet)
        .join(WorkoutExercise, WorkoutSet.workout_exercise_id == WorkoutExercise.id)
        .join(Exercise, WorkoutExercise.exercise_id == Exercise.id)
        .where(WorkoutSet.id == set_id)
    )
    result = await db.execute(stmt)
    exercise_category = result.scalar()
    return {"exercise_category": exercise_category} if exercise_category else None
    '''