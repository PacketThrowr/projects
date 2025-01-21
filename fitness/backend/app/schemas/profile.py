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
    height_cm: Optional[float] = None
    weight: List[WeightEntry]  # Historical weight entries
    country: str  # Determines units
    units: MeasurementSystem

    @root_validator(pre=True)
    def calculate_height_cm(cls, values):
        try:
            # Debugging input
            print("Validator Input:", values)

            units = values.get("units")
            height_feet = values.get("height_feet", 0)
            height_inches = values.get("height_inches", 0)
            height_cm = values.get("height_cm", 0)

            if units == "imperial":
                if height_feet or height_inches:
                    values["height_cm"] = (height_feet * 30.48) + (height_inches * 2.54)
                else:
                    raise ValueError("Height in feet or inches must be provided for imperial units.")
            elif units == "metric":
                if not height_cm or height_cm <= 0:
                    raise ValueError("Height in cm must be provided for metric units.")
                values["height_cm"] = height_cm
            else:
                raise ValueError("Units must be 'imperial' or 'metric'.")

            # Debugging output
            print("Validator Output:", values)
            return values

        except Exception as e:
            print("Error during validation:", e)
            raise ValueError(f"Validation error: {e}")

class ProfileCreate(ProfileBase):
    pass  # Extend the base ProfileBase

class ProfileUpdate(BaseModel):
    name: Optional[str]
    gender: Optional[str]
    height_feet: Optional[int]
    height_inches: Optional[int]
    country: Optional[str]
    units: Optional[MeasurementSystem]

    class Config:
        from_attributes = True

class Profile(ProfileBase):
    id: int  # This is to reflect the database column
    # Include any additional fields as required

class WeightEntryResponse(BaseModel):
    date: str
    value: float
    bmi: float

class ProfileResponse(BaseModel):
    id: int
    user_id: int
    name: str
    gender: str
    height_cm: float
    weight: List[WeightEntryResponse]
    country: str
    units: str

    class Config:
        orm_mode = True  # This enables ORM-to-Pydantic conversion
        from_attributes = True  # Required for from_orm in Pydantic v2