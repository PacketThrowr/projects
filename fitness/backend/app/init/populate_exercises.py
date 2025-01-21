from app.database import SessionLocal, engine
from app.models.exercise import Base, Exercise
from sqlalchemy.orm import sessionmaker

# Initial data for exercises
INITIAL_EXERCISES = [
    {"name": "Running", "type": "cardio", "description": "Outdoor running", "picture": None},
    {"name": "Bench Press", "type": "weights", "weight_type": "free_weights", "muscle_category": "Chest", "muscle_groups": "Chest,Shoulders,Triceps", "picture": None},
    # Add more exercises as needed
]

def populate_exercises():
    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Start a session
    Session = sessionmaker(bind=engine)
    db = Session()

    # Populate exercises
    for exercise in INITIAL_EXERCISES:
        if not db.query(Exercise).filter(Exercise.name == exercise["name"]).first():
            db.add(Exercise(**exercise))
    db.commit()
    db.close()

if __name__ == "__main__":
    populate_exercises()
