from sqlalchemy import Column, Integer, String, Date
from .database import Base

class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    date = Column(Date)
    duration = Column(Integer)  # Duration in minutes
    notes = Column(String, nullable=True)

