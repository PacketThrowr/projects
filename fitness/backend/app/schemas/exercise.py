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
    force: Optional[str] = None
    level: Optional[str] = None
    mechanic: Optional[str] = None
    equipment: Optional[str] = None
    primaryMuscles: Optional[List[str]] = None
    secondaryMuscles: Optional[List[str]] = None
    instructions: Optional[List[str]] = None
    category: Optional[str] = None
    picture: Optional[str] = None
    recorded_type: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    pass


class Exercise(ExerciseBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class ExerciseSchema(BaseModel):
    id: int
    name: str
    type: ExerciseType
    model_config = ConfigDict(from_attributes=True)