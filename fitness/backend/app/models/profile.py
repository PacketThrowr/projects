from sqlalchemy import Enum, Column, Integer, String, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum

class Gender(PyEnum):
    MALE = "male"
    FEMALE = "female"
    NOT_APPLICABLE = "not applicable"

class MeasurementSystem(PyEnum):
    METRIC = "metric"
    IMPERIAL = "imperial"

    def __str__(self):
        return self.value

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Link to User
    name = Column(String, nullable=False)
    gender = Column(Enum(Gender, name="gender"), nullable=False)
    height = Column(Float, nullable=False)  # Stored in cm
    weight = Column(JSON, nullable=False)  # Historical weights
    country = Column(String, nullable=False)
    units = Column(Enum(MeasurementSystem, name="measurementsystem"), nullable=False)
    progress_pictures = relationship("ProgressPicture", back_populates="profile", cascade="all, delete")

    user = relationship("User", back_populates="profile")
