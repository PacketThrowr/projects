from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from app.models.cardio import CardioSession, CardioHealthData, CardioGPSData
from app.schemas.cardio import CardioSessionCreate, CardioHealthDataCreate, CardioGPSDataCreate

async def get_cardio_sessions_for_profile(db: AsyncSession, profile_id: int) -> List[CardioSession]:
    query = (
        select(CardioSession)
        .where(CardioSession.profile_id == profile_id)
        .options(
            selectinload(CardioSession.health_data),
            selectinload(CardioSession.gps_data)
        )
    )
    result = await db.execute(query)
    return result.scalars().all()

async def create_cardio_session(db: AsyncSession, session: CardioSessionCreate) -> CardioSession:
    db_session = CardioSession(**session.model_dump())
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    
    # Explicitly load relationships
    await db.refresh(db_session, attribute_names=['health_data', 'gps_data'])
    return db_session

async def get_cardio_session_by_id(db: AsyncSession, session_id: int) -> Optional[CardioSession]:
   result = await db.execute(
       select(CardioSession).where(CardioSession.id == session_id)
   )
   return result.scalar_one_or_none()

async def add_health_data(db: AsyncSession, session_id: int, data: List[CardioHealthDataCreate]) -> List[CardioHealthData]:
   db_data = [CardioHealthData(**d.model_dump(), session_id=session_id) for d in data]
   db.add_all(db_data)
   await db.commit()
   return db_data

async def add_gps_data(db: AsyncSession, session_id: int, data: List[CardioGPSDataCreate]) -> List[CardioGPSData]:
   db_data = [CardioGPSData(**d.model_dump(), session_id=session_id) for d in data]
   db.add_all(db_data)
   await db.commit()
   return db_data

async def get_cardio_sessions(db: AsyncSession, profile_id: int, skip: int = 0, limit: int = 100) -> List[CardioSession]:
    return db.query(CardioSession).filter(CardioSession.profile_id == profile_id).offset(skip).limit(limit).all()

async def get_cardio_session(db: AsyncSession, session_id: int) -> Optional[CardioSession]:
    return db.query(CardioSession).filter(CardioSession.id == session_id).first()

async def update_cardio_session_status(db: AsyncSession, session_id: int, status: str) -> Optional[CardioSession]:
   stmt = (
       update(CardioSession)
       .where(CardioSession.id == session_id)
       .values(status=status)
       .returning(CardioSession)
   )
   result = await db.execute(stmt)
   await db.commit()
   session = result.scalar_one_or_none()
   
   if session:
       # Refresh and load relationships
       await db.refresh(session)
       await db.refresh(session, ['health_data', 'gps_data'])
   return session