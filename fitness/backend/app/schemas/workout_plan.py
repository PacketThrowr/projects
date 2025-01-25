from pydantic import BaseModel, model_validator, ConfigDict
from typing import List, Optional, ForwardRef
from enum import Enum

Exercise = ForwardRef('Exercise')
WorkoutPlanSet = ForwardRef('WorkoutPlanSet')
WorkoutPlanExercise = ForwardRef('WorkoutPlanExercise')

class WorkoutPlanSetBase(BaseModel):
    reps: Optional[int] = None
    weight: Optional[float] = None
    time: Optional[float] = None
    completed: bool = False

    @model_validator(mode="after")
    def validate_set(self) -> 'WorkoutPlanSetBase':
        # Remove strict validation or adjust the condition as necessary
        if self.reps is None and self.time is None:
            raise ValueError("Either 'reps' or 'time' must be provided.")
        return self

class WorkoutPlanSetCreate(WorkoutPlanSetBase):
    pass


class WorkoutPlanSet(WorkoutPlanSetBase):
    id: int
    exercise_id: int
    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanExerciseBase(BaseModel):
    exercise_id: int


class WorkoutPlanExerciseCreate(WorkoutPlanExerciseBase):
    sets: List[WorkoutPlanSetCreate] = []


class WorkoutPlanExercise(WorkoutPlanExerciseBase):
    id: int
    workout_plan_id: int
    exercise_id: int
    exercise: Optional['Exercise']  = None# Add if you want to include exercise details
    sets: List[WorkoutPlanSet] = []
    model_config = ConfigDict(from_attributes=True)


class WorkoutPlanBase(BaseModel):
    name: str
    description: Optional[str] = None


class WorkoutPlanCreate(WorkoutPlanBase):
    profile_id: int
    exercises: Optional[List[WorkoutPlanExerciseCreate]] = []


class WorkoutPlan(WorkoutPlanBase):
    id: int
    profile_id: int
    exercises: Optional[List[WorkoutPlanExercise]] = []
    model_config = ConfigDict(from_attributes=True)

class ExerciseAdd(BaseModel):
    exercise_id: int

# Set Update Schemas for Workout Plans
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

class WorkoutSetCreate(BaseModel):
    reps: int
    weight: Optional[float]
    time: Optional[float]
    completed: bool = False

class WorkoutPlanExerciseCreate(BaseModel):
    exercise_id: int
    sets: List[WorkoutSetCreate]

class Exercise(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    measurement_type: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

# Resolve forward references
WorkoutPlan.model_rebuild()
WorkoutPlanExercise.model_rebuild()
WorkoutPlanSet.model_rebuild()