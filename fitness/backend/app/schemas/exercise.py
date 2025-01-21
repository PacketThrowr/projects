from pydantic import BaseModel, Field, ValidationError, model_validator
from typing import Optional, List
from enum import Enum


# Define enumerations
class ExerciseType(str, Enum):
    cardio = "cardio"
    weights = "weights"


class WeightType(str, Enum):
    free_weights = "free_weights"
    machines = "machines"
    bodyweight = "bodyweight"


class MeasurementType(str, Enum):
    reps = "reps"
    time = "time"


# Base schema
class ExerciseBase(BaseModel):
    name: str
    picture: Optional[str] = None
    description: Optional[str] = None
    type: ExerciseType
    weight_type: Optional[WeightType] = None
    muscle_category: Optional[str] = None
    muscle_groups: Optional[List[str]] = None
    measurement_type: MeasurementType = MeasurementType.reps  # Default to 'reps'

    # Model validator for conditional fields
    @model_validator(mode="after")
    def validate_weight_fields(cls, values):
        if values.type == ExerciseType.weights:
            if not values.weight_type:
                raise ValueError("weight_type is required when type is 'weights'")
            if not values.muscle_category:
                raise ValueError("muscle_category is required when type is 'weights'")
            if not values.muscle_groups or not isinstance(values.muscle_groups, list):
                raise ValueError("muscle_groups must be a list when type is 'weights'")
        return values


class ExerciseCreate(ExerciseBase):
    pass


class Exercise(ExerciseBase):
    class Config:
        from_attributes = True
