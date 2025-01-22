from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import async_session_maker
from app.models.user import User
from app import crud
from app.auth.backend import current_active_user
from app.schemas.cardio import (
    CardioSession, 
    CardioSessionCreate,
    CardioHealthData,
    CardioHealthDataCreate,
    CardioGPSData, 
    CardioGPSDataCreate
)

router = APIRouter()

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

@router.post("/profiles/{profile_id}/cardio/", response_model=CardioSession)
async def create_cardio_session(
    profile_id: int,
    session: CardioSessionCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    session.profile_id = profile_id
    return await crud.create_cardio_session(db, session)

@router.get("/profiles/{profile_id}/cardio/", response_model=List[CardioSession])
async def get_cardio_sessions_for_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(current_active_user),
):
    db_profile = await crud.get_profile_by_id(db, profile_id)
    if not db_profile or db_profile.user_id != user.id:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return await crud.get_cardio_sessions_for_profile(db, profile_id)

@router.post("/profiles/{profile_id}/cardio/{session_id}/health", response_model=List[CardioHealthData])
async def add_health_data(
   profile_id: int,
   session_id: int,
   data: List[CardioHealthDataCreate],
   db: AsyncSession = Depends(get_db),
   user: User = Depends(current_active_user),
):
   db_profile = await crud.get_profile_by_id(db, profile_id)
   if not db_profile or db_profile.user_id != user.id:
       raise HTTPException(status_code=404, detail="Profile not found")
       
   session = await crud.get_cardio_session_by_id(db, session_id)
   if not session or session.profile_id != profile_id:
       raise HTTPException(status_code=404, detail="Session not found")
       
   return await crud.add_health_data(db, session_id, data)

@router.post("/profiles/{profile_id}/cardio/{session_id}/gps", response_model=List[CardioGPSData]) 
async def add_gps_data(
   profile_id: int,
   session_id: int,
   data: List[CardioGPSDataCreate],
   db: AsyncSession = Depends(get_db),
   user: User = Depends(current_active_user),
):
   db_profile = await crud.get_profile_by_id(db, profile_id)
   if not db_profile or db_profile.user_id != user.id:
       raise HTTPException(status_code=404, detail="Profile not found")
       
   session = await crud.get_cardio_session_by_id(db, session_id)
   if not session or session.profile_id != profile_id:
       raise HTTPException(status_code=404, detail="Session not found")
       
   return await crud.add_gps_data(db, session_id, data)

@router.patch("/profiles/{profile_id}/cardio/{session_id}/status", response_model=CardioSession)
async def update_session_status(
   profile_id: int,
   session_id: int,
   status: str,
   db: AsyncSession = Depends(get_db),
   user: User = Depends(current_active_user)
):
   db_profile = await crud.get_profile_by_id(db, profile_id)
   if not db_profile or db_profile.user_id != user.id:
       raise HTTPException(status_code=404, detail="Profile not found")

   session = await crud.get_cardio_session_by_id(db, session_id)
   if not session or session.profile_id != profile_id:
       raise HTTPException(status_code=404, detail="Session not found")

   return await crud.update_cardio_session_status(db, session_id, status)