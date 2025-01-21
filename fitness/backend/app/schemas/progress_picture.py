from pydantic import BaseModel
from datetime import date


class ProgressPictureBase(BaseModel):
    date: date
    weight: float
    image_path: str


class ProgressPictureCreate(BaseModel):
    date: date
    weight: float


class ProgressPicture(ProgressPictureBase):
    id: int
    profile_id: int

    class Config:
        from_attributes = True
