from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float
from sqlalchemy.orm import relationship
from app.database import Base


class ProgressPicture(Base):
    __tablename__ = "progress_pictures"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    weight = Column(Float, nullable=False)
    image_path = Column(String, nullable=False)

    profile = relationship("Profile", back_populates="progress_pictures")
