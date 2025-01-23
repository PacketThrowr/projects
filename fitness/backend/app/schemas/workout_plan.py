from pydantic import BaseModel, model_validator, ConfigDict
from typing import List, Optional
from enum import Enum

class WorkoutPlanSetBase(BaseModel):
    reps: Optional[int] = None
    weight: Optional[float] = None
    time: Optional[float] = None
    completed: bool = False


class WorkoutPlanSetCreate(WorkoutPlanSetBase):
    pass


class WorkoutPlanSet(WorkoutPlanSetBase):
    id: int
    exercise_id: int
    class Config:
        from_attributes = True


class WorkoutPlanExerciseBase(BaseModel):
    exercise_id: int


class WorkoutPlanExerciseCreate(WorkoutPlanExerciseBase):
    sets: List[WorkoutPlanSetCreate] = []


class WorkoutPlanExercise(WorkoutPlanExerciseBase):
    id: int
    sets: List[WorkoutPlanSet] = []
    class Config:
        from_attributes = True


class WorkoutPlanBase(BaseModel):
    name: str
    description: Optional[str] = None


class WorkoutPlanCreate(WorkoutPlanBase):
    profile_id: int
    exercises: List[WorkoutPlanExerciseCreate] = []


class WorkoutPlan(WorkoutPlanBase):
    id: int
    profile_id: int
    exercises: List[WorkoutPlanExercise] = []
    class Config:
        from_attributes = True

class WorkoutSetCreate(BaseModel):
    reps: int
    weight: Optional[float]
    time: Optional[float]
    completed: bool

class WorkoutPlanExerciseCreate(BaseModel):
    exercise_id: int
    sets: List[WorkoutSetCreate]

class WorkoutPlanCreate(BaseModel):
    name: str
    description: Optional[str]
    profile_id: int
    exercises: List[WorkoutPlanExerciseCreate] = []