from sqlalchemy import Column, Integer, String, Text, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base
from enum import Enum as PyEnum


# Define enumerations for type and weight type
class ExerciseType(PyEnum):
    CARDIO = "cardio"
    WEIGHTS = "weights"


class WeightType(PyEnum):
    FREE_WEIGHTS = "free_weights"
    MACHINES = "machines"
    BODYWEIGHT = "bodyweight"

class MeasurementType(PyEnum):
    REPS = "reps"
    TIME = "time"

class Exercise(Base):
    __tablename__ = "exercises"

    name = Column(String, primary_key=True, unique=True, index=True, nullable=False)
    picture = Column(String, nullable=True)  # Optional file location
    description = Column(Text, nullable=True)  # Optional
    type = Column(Enum(ExerciseType), nullable=False)  # Cardio or Weights
    weight_type = Column(Enum(WeightType), nullable=True)  # Required if type = Weights
    muscle_category = Column(String, nullable=True)  # Required if type = Weights
    muscle_groups = Column(String, nullable=True)  # Required if type = Weights
    measurement_type = Column(Enum(MeasurementType), nullable=False, default=MeasurementType.REPS)  # Reps or Time