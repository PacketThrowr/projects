from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.exercise import Exercise as ExerciseModel
from app.schemas.exercise import ExerciseCreate
from app.models.workout import Workout, WorkoutExercise, WorkoutSet
from app.schemas.workout import WorkoutCreate
from app.models.profile import Profile, Gender, MeasurementSystem
from app.schemas.profile import ProfileBase, WeightEntry, ProfileCreate, ProfileUpdate,  ProfileResponse
from app.utils import get_units_for_country
from app.models.progress_picture import ProgressPicture
from datetime import date
from sqlalchemy.future import select
from datetime import datetime

# Get all exercises
def get_exercises(db: Session, skip: int = 0, limit: int = 10):
    return db.query(ExerciseModel).offset(skip).limit(limit).all()

# Get exercise by name
def get_exercise_by_name(db: Session, name: str):
    return db.query(Exercise).filter(Exercise.name == name).first()

# Create a new exercise
def create_exercise(db: Session, exercise: ExerciseCreate):
    db_exercise = db.query(Exercise).filter(Exercise.name == exercise.name).first()
    if db_exercise:
        raise ValueError(f"Exercise with name '{exercise.name}' already exists")
    new_exercise = Exercise(**exercise.dict())
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return new_exercise

# Update an existing exercise
def update_exercise(db: Session, exercise_id: int, updated_exercise: ExerciseCreate):
    db_exercise = db.query(ExerciseModel).filter(ExerciseModel.id == exercise_id).first()
    if not db_exercise:
        return None
    db_exercise.name = updated_exercise.name
    db_exercise.description = updated_exercise.description
    db_exercise.muscle_group = updated_exercise.muscle_group
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

# Delete an exercise
def delete_exercise(db: Session, exercise_id: int):
    db_exercise = db.query(ExerciseModel).filter(ExerciseModel.id == exercise_id).first()
    if not db_exercise:
        return None
    db.delete(db_exercise)
    db.commit()
    return True

def create_workout(db: Session, workout: WorkoutCreate):
    db_workout = Workout(name=workout.name, description=workout.description)
    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)

    for exercise in workout.exercises:
        db_workout_exercise = WorkoutExercise(
            workout_id=db_workout.id, exercise_id=exercise.exercise_id
        )
        db.add(db_workout_exercise)
        db.commit()
        db.refresh(db_workout_exercise)

        for set_data in exercise.sets:
            db_set = WorkoutSet(
                workout_exercise_id=db_workout_exercise.id,
                reps=set_data.reps,
                weight=set_data.weight,
                time=set_data.time,
                completed=set_data.completed,
            )
            db.add(db_set)
            db.commit()
    return db_workout


def get_workout(db: Session, workout_id: int):
    return db.query(Workout).filter(Workout.id == workout_id).first()


def get_workouts(db: Session):
    return db.query(Workout).all()


def update_workout_set(db: Session, set_id: int, updates: dict):
    db_set = db.query(WorkoutSet).filter(WorkoutSet.id == set_id).first()
    if not db_set:
        return None
    for key, value in updates.items():
        setattr(db_set, key, value)
    db.commit()
    db.refresh(db_set)
    return db_set

def delete_workout(db: Session, workout_id: int):
    db_workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not db_workout:
        return None
    db.delete(db_workout)
    db.commit()
    return True

def add_exercise_to_workout(db: Session, workout_id: int, exercise_name: str):
    # Validate workout existence
    db_workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not db_workout:
        raise ValueError(f"Workout with ID {workout_id} does not exist")

    # Validate exercise existence
    db_exercise = db.query(Exercise).filter(Exercise.name == exercise_name).first()
    if not db_exercise:
        raise ValueError(f"Exercise with name '{exercise_name}' does not exist")

    # Add exercise to workout
    db_workout_exercise = WorkoutExercise(
        workout_id=workout_id,
        exercise_name=exercise_name
    )
    db.add(db_workout_exercise)
    db.commit()
    db.refresh(db_workout_exercise)

    return db_workout_exercise