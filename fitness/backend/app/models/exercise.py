from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base
from enum import Enum as PyEnum
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from .cardio import CardioSession

# Define enumerations for type and weight type
class ExerciseType(PyEnum):
    CARDIO = "CARDIO"
    WEIGHTS = "WEIGHTS"


class WeightType(PyEnum):
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


class MeasurementType(PyEnum):
    REPS = "reps"
    TIME = "time"

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    picture = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=False)
    weight_type = Column(String, nullable=True)
    muscle_category = Column(String, nullable=True)
    muscle_groups = Column(JSON, nullable=True)
    measurement_type = Column(String, nullable=False)

    workout_exercises = relationship("WorkoutExercise", back_populates="exercise")
    cardio_sessions = relationship("CardioSession", back_populates="exercise", cascade="all, delete-orphan")