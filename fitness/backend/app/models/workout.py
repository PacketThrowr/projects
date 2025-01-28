from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, Enum, Text, String
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    exercises = relationship("WorkoutExercise", back_populates="workout", cascade="all, delete-orphan")
    date = Column(String, nullable=False)
    start_time = Column(String, nullable=True)
    end_time = Column(String, nullable=True)

    profile = relationship("Profile", back_populates="workouts")

class WorkoutExercise(Base):
    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id", ondelete="CASCADE"))
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"))
    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_exercises")
    sets = relationship("WorkoutSet", back_populates="exercise", cascade="all, delete-orphan", lazy="selectin")

class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("workout_exercises.id", ondelete="CASCADE"))
    reps = Column(Integer, nullable=True, default=0)  # Default to 0 if not provided
    weight = Column(Float, nullable=True, default=0.0)
    time = Column(Float, nullable=True, default=0.0)
    completed = Column(Integer, default=0)  # Boolean represented as 0/1
    exercise = relationship("WorkoutExercise", back_populates="sets")
