from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from app.models.progress_picture import ProgressPicture
from datetime import date


async def add_progress_picture(
    db: AsyncSession, profile_id: int, date: date, weight: float, image_path: str
) -> ProgressPicture:
    db_picture = ProgressPicture(
        profile_id=profile_id,
        date=date,
        weight=weight,
        image_path=image_path,
    )
    db.add(db_picture)
    await db.commit()
    await db.refresh(db_picture)
    return db_picture


async def get_progress_pictures(db: AsyncSession, profile_id: int) -> list[ProgressPicture]:
    result = await db.execute(select(ProgressPicture).where(ProgressPicture.profile_id == profile_id))
    return result.scalars().all()


async def get_progress_picture_by_id(db: AsyncSession, picture_id: int):
    result = await db.execute(select(ProgressPicture).where(ProgressPicture.id == picture_id))
    return result.scalars().first()

async def delete_progress_picture(db: AsyncSession, picture_id: int) -> ProgressPicture | None:
    db_picture = await get_progress_picture_by_id(db, picture_id)
    if db_picture:
        await db.delete(db_picture)
        await db.commit()
    return db_picture