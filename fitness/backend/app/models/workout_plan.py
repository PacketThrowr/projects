from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, Enum, Text, String
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    profile = relationship("Profile", back_populates="workout_plans")
    exercises = relationship(
        "WorkoutPlanExercise", 
        back_populates="workout_plan", 
        cascade="all, delete-orphan", 
        lazy="selectin"
    )
class WorkoutPlanExercise(Base):
    __tablename__ = "workout_plan_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"))
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"))
    workout_plan = relationship("WorkoutPlan", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_plan_exercises", lazy="joined")
    sets = relationship("WorkoutPlanSet", back_populates="exercise", cascade="all, delete-orphan",lazy="selectin")


class WorkoutPlanSet(Base):
    __tablename__ = "workout_plan_sets"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("workout_plan_exercises.id", ondelete="CASCADE"))
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    time = Column(Float, nullable=True)
    completed = Column(Boolean, default=False)
    exercise = relationship("WorkoutPlanExercise", back_populates="sets")