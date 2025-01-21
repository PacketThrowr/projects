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
from app.models.user import User
from app.schemas.user import UserCreate
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

async def create_profile(db: Session, profile_data: ProfileBase, user_id: int):
    # Validate and process the input data
    validated_data = ProfileBase(**profile_data.dict())

    # Extract necessary data
    units_enum = validated_data.units.value
    gender_enum = validated_data.gender.value
    height_cm = validated_data.height_cm

    # Process weight entries
    weight_data = []
    for entry in validated_data.weight:
        weight_kg = (
            round(entry.value * 0.453592, 2) if units_enum == "imperial" else entry.value
        )
        bmi = round(weight_kg / ((height_cm / 100) ** 2), 2)
        weight_data.append({
            "date": entry.date,
            "value": weight_kg,
            "bmi": bmi,
        })

    # Create the new profile instance
    new_profile = Profile(
        user_id=user_id,
        name=validated_data.name,
        gender=gender_enum,
        height_cm=height_cm,
        weight=weight_data,
        country=validated_data.country,
        units=units_enum,
    )

    # Save to the database
    db.add(new_profile)
    await db.commit()
    await db.refresh(new_profile)

    # Convert SQLAlchemy model to Pydantic response
    return ProfileResponse.from_orm(new_profile)




async def get_profiles_for_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(Profile).filter(Profile.user_id == user_id))
    return result.scalars().all()


async def get_profile_by_id(db: AsyncSession, profile_id: int):
    # Use select() with AsyncSession for async queries
    result = await db.execute(select(Profile).filter(Profile.id == profile_id))
    return result.scalars().first()  # Use scalars() to get the first result

async def update_profile(db: AsyncSession, profile_id: int, profile_update: ProfileUpdate):
    # Fetch the profile by ID asynchronously
    db_profile = await get_profile_by_id(db, profile_id)
    if not db_profile:
        return None

    # Update height if provided
    if profile_update.height_feet is not None and profile_update.height_inches is not None:
        db_profile.height = (profile_update.height_feet * 30.48) + (profile_update.height_inches * 2.54)

    # Update weight entries with recalculated BMI
    for entry in db_profile.weight:
        weight_kg = entry["value"]
        if db_profile.units == MeasurementSystem.IMPERIAL:
            weight_kg = round(weight_kg * 0.453592, 2)
        entry["bmi"] = calculate_bmi(weight_kg, db_profile.height)

    db_profile.name = profile_update.name
    db_profile.gender = profile_update.gender
    db_profile.country = profile_update.country
    db_profile.units = get_units_for_country(profile_update.country)

    # Asynchronous commit
    await db.commit()
    await db.refresh(db_profile)
    return db_profile

def delete_profile(db: Session, profile_id: int):
    db_profile = get_profile_by_id(db, profile_id)
    if not db_profile:
        return None

    db.delete(db_profile)
    db.commit()
    return True

async def get_weights_for_profile(db: AsyncSession, db_profile: Profile):
    # Ensure the profile has a valid weights field
    weights = db_profile.weight or []
    return weights
    
async def delete_weight_entry(db: AsyncSession, db_profile: Profile, date: str):
    from datetime import datetime

    # Parse the date to validate the format
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")

    # Find and remove the weight entry with the specified date
    updated_weights = [
        weight for weight in db_profile.weight
        if weight["date"] != target_date.strftime("%Y-%m-%d")
    ]

    if len(updated_weights) == len(db_profile.weight):  # No change means entry not found
        raise ValueError(f"No weight entry found for date {date}")

    # Update the profile
    db_profile.weight = updated_weights

    # Commit and refresh
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)

    return db_profile

async def update_weight_entry(
    db: AsyncSession, db_profile: Profile, date: str, new_weight: WeightEntry
):
    from datetime import datetime

    # Parse the date to validate the format
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")

    # Ensure the weight entry exists for the specified date
    existing_weights = db_profile.weight or []
    weight_entry = next(
        (entry for entry in existing_weights if entry["date"] == target_date.strftime("%Y-%m-%d")), None
    )
    if not weight_entry:
        raise ValueError(f"No weight entry found for date {date}")

    # Convert weight to kilograms if in imperial units
    weight_kg = new_weight.value
    if db_profile.units == "imperial":
        weight_kg = round(weight_kg * 0.453592, 2)  # Convert lbs to kg

    # Calculate BMI
    height_m = db_profile.height_cm / 100  # Convert height from cm to meters
    bmi = round(weight_kg / (height_m ** 2), 2)

    # Update the weight entry
    weight_entry["value"] = new_weight.value  # Store the original input value
    weight_entry["bmi"] = bmi

    # Update the profile
    db_profile.weight = existing_weights

    # Commit and refresh
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)

    return db_profile

def calculate_bmi(weight: float, height_cm: float) -> float:
    """
    Calculate BMI using weight (kg) and height (cm).
    """
    height_m = height_cm / 100  # Convert cm to meters
    return round(weight / (height_m ** 2), 2)  # Round to 2 decimal places


async def add_weight_to_profile(db: AsyncSession, db_profile: Profile, weight: WeightEntry):

    # Validate the weight date format
    try:
        weight_date = datetime.strptime(weight.date, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Expected format: YYYY-MM-DD")

    # Check if the weight for this date already exists
    existing_weights = db_profile.weight or []  # Ensure weights are treated as a list
    if any(entry["date"] == weight.date for entry in existing_weights):
        raise ValueError(f"Weight entry for date {weight.date} already exists")

    # Convert weight to kilograms if in imperial units
    weight_kg = weight.value
    if db_profile.units == "imperial":
        weight_kg = round(weight_kg * 0.453592, 2)  # Convert lbs to kg

    # Calculate BMI
    height_m = db_profile.height_cm / 100  # Convert height from cm to meters
    bmi = round(weight_kg / (height_m ** 2), 2)

    # Add the new weight entry
    new_weight_entry = {
        "date": weight.date,
        "value": weight_kg,  # Store the weight in kilograms
        "bmi": bmi,
    }
    db_profile.weight = existing_weights + [new_weight_entry]  # Append to the weight list

    # Commit and refresh
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)

    return db_profile

def add_progress_picture(db: Session, profile_id: int, date: date, weight: float, image_path: str):
    db_picture = ProgressPicture(
        profile_id=profile_id,
        date=date,
        weight=weight,
        image_path=image_path,
    )
    db.add(db_picture)
    db.commit()
    db.refresh(db_picture)
    return db_picture


def get_progress_pictures(db: Session, profile_id: int):
    return db.query(ProgressPicture).filter(ProgressPicture.profile_id == profile_id).all()


def delete_progress_picture(db: Session, picture_id: int):
    db_picture = db.query(ProgressPicture).filter(ProgressPicture.id == picture_id).first()
    if db_picture:
        db.delete(db_picture)
        db.commit()
    return db_picture

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


async def create_user(db: AsyncSession, username: str, email: str, password: str):
    new_user = User(
        username=username,
        email=email,
        hashed_password=password  # Hash this password before storing!
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user