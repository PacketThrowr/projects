from pydantic import BaseModel, root_validator
from enum import Enum
from typing import Optional, List

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NOT_APPLICABLE = "not applicable"

class MeasurementSystem(Enum):
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

    @root_validator(pre=True)
    def validate_and_transform(cls, values):
        # Ensure gender is passed as a string (e.g., 'male', 'female', 'not_applicable')
        if isinstance(values.get("gender"), str):
            values["gender"] = Gender[values["gender"].upper()]
        
        # Ensure units are passed as a string (e.g., 'imperial', 'metric')
        if isinstance(values.get("units"), str):
            values["units"] = MeasurementSystem[values["units"].upper()]
        
        return values

class ProfileCreate(ProfileBase):
    pass  # Extend the base ProfileBase

class ProfileUpdate(ProfileBase):
    pass  # Optionally extend with update logic

class Profile(ProfileBase):
    id: int  # This is to reflect the database column
    # Include any additional fields as required