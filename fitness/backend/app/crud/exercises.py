from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseCreate, MeasurementType, WeightType, ExerciseType
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
            description=exercise.description,
            type=exercise.type.value,  # Use the enum value directly
            weight_type=exercise.weight_type.value if exercise.weight_type else None,
            muscle_category=exercise.muscle_category,
            muscle_groups=exercise.muscle_groups,
            measurement_type=exercise.measurement_type.value
        )
        db.add(db_exercise)
        await db.commit()
        await db.refresh(db_exercise)
        return db_exercise
    except Exception as e:
        await db.rollback()
        raise ValueError(f"Error creating exercise: {str(e)}")



async def update_exercise(db: AsyncSession, exercise_id: int, updated_exercise: ExerciseCreate):
    # Changed to search by ID instead of name
    stmt = select(Exercise).where(Exercise.id == exercise_id)
    result = await db.execute(stmt)
    db_exercise = result.scalars().first()
    
    if not db_exercise:
        return None
    
    # Update the exercise with the new values
    for field, value in updated_exercise.model_dump(exclude_unset=True).items():  # Changed from dict() to model_dump()
        if field == 'muscle_groups' and value is not None:
            value = value
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

async def get_set_exercise_type(db: AsyncSession, set_id: int):
    """Get the exercise type for a given set"""
    stmt = (
        select(Exercise.type)
        .select_from(WorkoutSet)
        .join(WorkoutExercise, WorkoutSet.workout_exercise_id == WorkoutExercise.id)  # Change to workout_exercise_id
        .join(Exercise, WorkoutExercise.exercise_id == Exercise.id)
        .where(WorkoutSet.id == set_id)
    )
    result = await db.execute(stmt)
    exercise_type = result.scalar()
    return {"exercise_type": exercise_type} if exercise_type else None