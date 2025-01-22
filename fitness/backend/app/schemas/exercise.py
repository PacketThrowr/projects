from pydantic import BaseModel, Field, ValidationError, model_validator, root_validator, ConfigDict
from typing import Optional, List
from enum import Enum


# Define enumerations
class ExerciseType(str, Enum):
    CARDIO = "CARDIO"
    WEIGHTS = "WEIGHTS"

class WeightType(str, Enum):
    BARBELL = "BARBELL"
    DUMBBELL = "DUMBBELL"
    KETTLEBELL = "KETTLEBELL"
    CABLE = "CABLE"
    MACHINE = "MACHINE"
    BODYWEIGHT = "BODYWEIGHT"
    RESISTANCE_BAND = "RESISTANCE_BAND"
    SMITH_MACHINE = "SMITH_MACHINE"
    PLATE_LOADED = "PLATE_LOADED"
    OTHER = "OTHER"

class MeasurementType(str, Enum):
    REPS = "REPS"
    TIME = "TIME"


# Base schema
class ExerciseBase(BaseModel):
    name: str
    picture: Optional[str] = None
    description: Optional[str] = None
    type: ExerciseType
    weight_type: Optional[WeightType] = None
    muscle_category: Optional[str] = None
    muscle_groups: Optional[List[str]] = None
    measurement_type: MeasurementType

    @model_validator(mode='before')
    @classmethod
    def normalize_enum_values(cls, data):
        """
        Ensure enum fields are normalized correctly.
        """
        if not isinstance(data, dict):
            return data
            
        if isinstance(data.get("weight_type"), str):
            data["weight_type"] = data["weight_type"].upper()
        if isinstance(data.get("type"), str):
            data["type"] = data["type"].upper()
        if isinstance(data.get("measurement_type"), str):
            data["measurement_type"] = data["measurement_type"].upper()
        return data




class ExerciseCreate(ExerciseBase):
    pass


class Exercise(ExerciseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)