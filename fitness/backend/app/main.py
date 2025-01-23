from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers.exercises import router as exercises_router
from app.routers.workouts import router as workouts_router
from app.routers.profiles import router as profiles_router
from app.routers.progress_pictures import router as progress_pictures_router
from app.routers.users import router as users_router
from app.routers.auth import router as auth_router
from app.routers.cardio import router as cardio_router
from app.routers.workout_plans import router as workout_plans_router
from app.database import engine
from app.models import Base  # Import Base to include all models
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://10.1.10.168:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the media directory for static file serving
app.mount("/media", StaticFiles(directory="media"), name="media")


# Asynchronous function to create tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Startup event to initialize the database
@app.on_event("startup")
async def on_startup():
    await create_tables()

# Include routers for exercises and workouts
app.include_router(exercises_router, prefix="/api", tags=["exercises"])
app.include_router(workouts_router, prefix="/api", tags=["workouts"])
app.include_router(profiles_router, prefix="/api", tags=["profiles"])
app.include_router(progress_pictures_router, prefix="/api", tags=["progress_pictures"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(cardio_router, prefix="/api", tags=["cardio"])
app.include_router(auth_router)
app.include_router(workout_plans_router, prefix="/api", tags=["workout_plans"])
@app.get("/")
def read_root():
    return {"message": "Welcome to the Workout Tracker API"}
