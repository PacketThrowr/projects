from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app import crud

COUNTRY_UNITS_MAP = {
    "US": "imperial",
    "UK": "imperial",
    "CA": "imperial",
    "AU": "metric",
    "IN": "metric",
    "FR": "metric",
    "DE": "metric",
    # Add more countries as needed
}

def get_units_for_country(country: str) -> str:
    return COUNTRY_UNITS_MAP.get(country.upper(), "metric")  # Default to metric

async def validate_user_profile(db: AsyncSession, user: User, profile_id: int):
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile