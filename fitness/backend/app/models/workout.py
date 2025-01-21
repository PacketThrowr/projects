from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    exercises = relationship("WorkoutExercise", back_populates="workout")


class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id", ondelete="CASCADE"), nullable=False)
    exercise_name = Column(String, ForeignKey("exercises.name", ondelete="CASCADE"), nullable=False)
    workout = relationship("Workout", back_populates="exercises")
    sets = relationship("WorkoutSet", back_populates="workout_exercise")


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_exercise_id = Column(Integer, ForeignKey("workout_exercises.id", ondelete="CASCADE"), nullable=False)
    reps = Column(Integer, nullable=True)  # Number of reps (optional if time-based)
    weight = Column(Float, nullable=True)  # Weight used (optional if time-based)
    time = Column(Float, nullable=True)  # Time duration in seconds (optional if reps-based)
    completed = Column(Boolean, default=False)  # Mark set as completed
    workout_exercise = relationship("WorkoutExercise", back_populates="sets")
