import json

def determine_record_type(exercise):
    isStatic = exercise['force'] == 'static'
    isStretching = exercise['category'] == 'stretching'
    isCardio = exercise['category'] == 'cardio'
    
    if isStatic or isStretching or isCardio:
        return "TIME"
    return "REPS"

# Read the input file
with open('/home/jgudgeon/js/exercises.json/exercises.json', 'r') as file:
    exercises = json.load(file)

# Add recorded_type to each exercise
updated_exercises = [
    {**exercise, 'recorded_type': determine_record_type(exercise)}
    for exercise in exercises
]

# Write the updated exercises to a new file
with open('exercises_updated.json', 'w') as file:
    json.dump(updated_exercises, file, indent=2)