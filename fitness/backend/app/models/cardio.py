from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Float, Enum, Text, String
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum

class CardioSession(Base):
    __tablename__ = "cardio_sessions"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id", ondelete="CASCADE"))
    duration = Column(Float, nullable=False)
    type = Column(String, nullable=False, default ="outdoor")  # 'indoor' or 'outdoor'
    status = Column(String, default="pending")
    
    profile = relationship("Profile", back_populates="cardio_sessions")
    exercise = relationship("Exercise", back_populates="cardio_sessions")
    health_data = relationship("CardioHealthData", back_populates="session", cascade="all, delete-orphan")
    gps_data = relationship("CardioGPSData", back_populates="session", cascade="all, delete-orphan")
    exercise = relationship("Exercise", back_populates="cardio_sessions")

class CardioHealthData(Base):
    __tablename__ = "cardio_health_data"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("cardio_sessions.id", ondelete="CASCADE"))
    heart_rate = Column(Integer)
    calories = Column(Float)
    steps = Column(Integer)
    distance = Column(Float)
    timestamp = Column(Float, nullable=False)
    
    session = relationship("CardioSession", back_populates="health_data")

class CardioGPSData(Base):
    __tablename__ = "cardio_gps_data"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("cardio_sessions.id", ondelete="CASCADE"))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    elevation = Column(Float)
    timestamp = Column(Float, nullable=False)
    
    session = relationship("CardioSession", back_populates="gps_data")
