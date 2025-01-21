from pydantic import BaseModel, root_validator
from enum import Enum
from typing import Optional, List

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NOT_APPLICABLE = "not applicable"

class MeasurementSystem(str, Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"

class WeightEntry(BaseModel):
    date: str
    value: float
    bmi: float

class ProfileBase(BaseModel):
    name: str
    gender: Gender
    height_feet: Optional[int] = None  # User input in feet
    height_inches: Optional[int] = None  # User input in inches
    weight: List[WeightEntry]  # Historical weight entries
    country: str  # Determines units
    units: MeasurementSystem

class ProfileCreate(ProfileBase):
    pass  # Extend the base ProfileBase

class ProfileUpdate(ProfileBase):
    name: str
    gender: str
    height_feet: int = None
    height_inches: int = None
    country: str
    units: str
    weight: list[WeightEntry]

class Profile(ProfileBase):
    id: int  # This is to reflect the database column
    # Include any additional fields as required