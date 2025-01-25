from pydantic import BaseModel, model_validator, ConfigDict, Field
from typing import List, Optional
from enum import Enum

# Base set schemas
class WorkoutSetBase(BaseModel):
    reps: Optional[int] = None
    weight: Optional[float] = None
    time: Optional[float] = None
    completed: bool = False

    @model_validator(mode="after")
    def validate_reps_and_time(self):
        # Both `reps` and `time` can be 0, but they cannot both be None
        if self.reps is None and self.time is None:
            raise ValueError("Either 'reps' or 'time' must be provided (not both null).")
        return self

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
    date: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None

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
    completed: Optional[bool] = False

class WeightSetUpdate(SetBaseUpdate):
    reps: Optional[int] = Field(None, description="Number of repetitions")
    weight: Optional[float] = Field(None, description="Weight lifted")
    time: Optional[float] = Field(None, description="Time for exercise")
    completed: bool = Field(False, description="Whether the set is completed")

class CardioSetUpdate(SetBaseUpdate):
    distance: Optional[float] = None
    completed: bool = False
        
class SetUpdate(BaseModel):
    type: SetType
    data: WeightSetUpdate | CardioSetUpdate

class WorkoutExerciseSchema(BaseModel):
    id: int
    exercise_id: int
    workout_id: int
    sets: List[WorkoutSet] = []
    model_config = ConfigDict(from_attributes=True)