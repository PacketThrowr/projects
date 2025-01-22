from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class CardioSessionBase(BaseModel):
    exercise_id: int
    duration: float
    type: str
    status: str = "pending"

class CardioSessionCreate(CardioSessionBase):
    profile_id: int

class CardioHealthDataCreate(BaseModel):
    heart_rate: Optional[int] = None
    calories: Optional[float] = None
    steps: Optional[int] = None
    distance: Optional[float] = None
    timestamp: float

class CardioGPSDataCreate(BaseModel):
    latitude: float
    longitude: float
    elevation: Optional[float] = None
    timestamp: float

class CardioHealthData(CardioHealthDataCreate):
    id: int
    session_id: int
    
    model_config = ConfigDict(from_attributes=True)

class CardioGPSData(CardioGPSDataCreate):
    id: int
    session_id: int
    
    model_config = ConfigDict(from_attributes=True)

class CardioSession(CardioSessionBase):
    id: int
    profile_id: int
    health_data: List[CardioHealthData] = []
    gps_data: List[CardioGPSData] = []
    
    model_config = ConfigDict(from_attributes=True)