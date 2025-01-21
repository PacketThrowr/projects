from pydantic import BaseModel
from typing import List, Optional


class WorkoutSetBase(BaseModel):
    reps: Optional[int] = None
    weight: Optional[float] = None
    time: Optional[float] = None
    completed: bool = False


class WorkoutSetCreate(WorkoutSetBase):
    pass


class WorkoutSet(WorkoutSetBase):
    id: int

    class Config:
        from_attributes = True


class WorkoutExerciseBase(BaseModel):
    exercise_id: int  # ID of the associated exercise


class WorkoutExerciseCreate(WorkoutExerciseBase):
    sets: List[WorkoutSetCreate] = []  # Initial sets


class WorkoutExercise(WorkoutExerciseBase):
    id: int
    sets: List[WorkoutSet] = []

    class Config:
        from_attributes = True


class WorkoutBase(BaseModel):
    name: str
    description: Optional[str] = None


class WorkoutCreate(WorkoutBase):
    exercises: List[WorkoutExerciseCreate] = []


class Workout(WorkoutBase):
    id: int
    exercises: List[WorkoutExercise] = []

    class Config:
        from_attributes = True
