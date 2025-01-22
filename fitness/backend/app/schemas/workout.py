from pydantic import BaseModel, model_validator
from typing import List, Optional
from enum import Enum

# Base set schemas
class WorkoutSetBase(BaseModel):
    reps: Optional[int] = None
    weight: Optional[float] = None
    time: Optional[float] = None
    completed: bool = False

    @model_validator(mode='after')
    def validate_set(self) -> 'WorkoutSetBase':
        values = self
        if not values.reps and not values.time:
            raise ValueError("Either 'reps' or 'time' must be provided.")
        return values

class WorkoutSetCreate(WorkoutSetBase):
    pass

class WorkoutSet(WorkoutSetBase):
    id: int
    exercise_id: int
    class Config:
        from_attributes = True

# Exercise schemas
class WorkoutExerciseBase(BaseModel):
    exercise_id: int

class WorkoutExerciseCreate(WorkoutExerciseBase):
    sets: List[WorkoutSetCreate] = []

class WorkoutExercise(WorkoutExerciseBase):
    id: int
    sets: List[WorkoutSet] = []

    class Config:
        from_attributes = True

# Workout schemas
class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkoutCreate(WorkoutBase):
    profile_id: int
    exercises: List[WorkoutExerciseCreate] = []

class Workout(WorkoutBase):
    id: int
    profile_id: int
    exercises: List[WorkoutExercise] = []

    class Config:
        from_attributes = True

# Exercise addition schema
class ExerciseAdd(BaseModel):
    exercise_name: str

# Set update schemas
class SetType(str, Enum):
    WEIGHT = "WEIGHT"
    CARDIO = "CARDIO"

class SetBaseUpdate(BaseModel):
    completed: Optional[bool] = None

class WeightSetUpdate(SetBaseUpdate):
    weight: Optional[float] = None
    reps: Optional[int] = None

    @model_validator(mode='after')
    def validate_weight_set(self) -> 'WeightSetUpdate':
        if not self.weight and not self.reps and self.completed is None:
            raise ValueError("At least one field must be provided")
        return self

class CardioSetUpdate(SetBaseUpdate):
    time: Optional[float] = None

    @model_validator(mode='after')
    def validate_cardio_set(self) -> 'CardioSetUpdate':
        if not self.time and self.completed is None:
            raise ValueError("At least one field must be provided")
        return self
        
class SetUpdate(BaseModel):
    type: SetType
    data: WeightSetUpdate | CardioSetUpdate