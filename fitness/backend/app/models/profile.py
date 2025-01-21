from sqlalchemy import Enum, Column, Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    NOT_APPLICABLE = "not applicable"

class MeasurementSystem(Enum):
    METRIC = "metric"
    IMPERIAL = "imperial"

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Link to User
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    height = Column(Float, nullable=False)  # Stored in cm
    weight = Column(JSON, nullable=False)  # Historical weights
    country = Column(String, nullable=False)
    units = Column(String, nullable=False)
    progress_pictures = relationship("ProgressPicture", back_populates="profile", cascade="all, delete")

    user = relationship("User", back_populates="profile")
