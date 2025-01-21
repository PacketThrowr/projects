from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.models.profile import Profile, Gender, MeasurementSystem
from app.schemas.profile import ProfileBase, WeightEntry, ProfileCreate, ProfileUpdate,  ProfileResponse
from app.utils import get_units_for_country
from sqlalchemy.orm.attributes import flag_modified

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
    # Fetch the profile by ID
    db_profile = await get_profile_by_id(db, profile_id)
    if not db_profile:
        raise ValueError(f"Profile with ID {profile_id} does not exist")

    # Update height if both feet and inches are provided
    if profile_update.height_feet is not None and profile_update.height_inches is not None:
        db_profile.height_cm = (profile_update.height_feet * 30.48) + (profile_update.height_inches * 2.54)

    # Update other fields
    if profile_update.name:
        db_profile.name = profile_update.name
    if profile_update.gender:
        db_profile.gender = profile_update.gender
    if profile_update.country:
        db_profile.country = profile_update.country
        db_profile.units = get_units_for_country(profile_update.country)  # Update units based on the country

    # Commit changes
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)

    return db_profile

async def delete_profile(db: AsyncSession, profile_id: int):
    db_profile = await db.execute(
        select(Profile).filter(Profile.id == profile_id)
    )
    db_profile = db_profile.scalars().first()

    if not db_profile:
        return False

    await db.delete(db_profile)
    await db.commit()
    return True

async def get_weights_for_profile(db: AsyncSession, db_profile: Profile):
    # Ensure the profile has a valid weights field
    weights = db_profile.weight or []
    return weights

async def delete_weight_entry(db: AsyncSession, db_profile: Profile, date: str):
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
        weight_kg = round(new_weight.value * 0.453592, 2)  # Convert lbs to kg

    # Calculate BMI
    height_m = db_profile.height_cm / 100  # Convert height from cm to meters
    bmi = round(weight_kg / (height_m ** 2), 2)

    # Update the weight entry
    weight_entry["value"] = weight_kg  # Store the weight in kilograms
    weight_entry["bmi"] = bmi

    # Update the profile weights
    db_profile.weight = existing_weights  # Reassign the list to trigger SQLAlchemy tracking
    flag_modified(db_profile, "weight")  # Mark the JSON field as modified

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