<template>
  <div class="workout-page">
    <!-- Workout Header -->
    <header class="workout-header">
      <h1>{{ workout.name }}</h1>
      <p>{{ workout.description }}</p>
      <p>
        <strong>Start Time:</strong> {{ workout.start_time || "Not started yet" }}
      </p>
      <button @click="endWorkout" class="end-button">End Workout</button>
    </header>

    <!-- Instructions Modal -->
    <div v-if="showInstructions" class="instructions-modal">
      <div class="instructions-content">
        <div class="instructions-header">
          <h3>Exercise Instructions</h3>
          <button @click="closeInstructions" class="close-button">&times;</button>
        </div>
        <div class="instructions-body">
          <p>{{ currentInstructions }}</p>
        </div>
      </div>
    </div>

    <!-- Exercises Section -->
    <section v-if="workout.exercises && workout.exercises.length > 0" class="exercises-section">
      <h2>Exercises</h2>
      <div v-for="exercise in workout.exercises" :key="exercise.id" class="exercise-block">
        <div class="exercise-header">
          <h3>{{ exercise.exercise.name }}</h3>
          <button 
            @click="showInstructionsFor(exercise)" 
            class="instructions-button"
          >
            Instructions
          </button>
        </div>
        
        <!-- Sets Table -->
        <div class="sets-table">
          <div class="table-header">
            <div class="header-cell">Set</div>
            <div class="header-cell">Weight (lbs)</div>
            <div class="header-cell">Reps</div>
            <div class="header-cell">Time (s)</div>
            <div class="header-cell">Complete</div>
            <div class="header-cell">Actions</div>
          </div>
          <div 
            v-for="(set, index) in exercise.sets" 
            :key="set.id" 
            class="table-row"
          >
            <div class="cell">{{ index + 1 }}</div>
            <div class="cell">
              <input 
                type="number" 
                v-model="set.weight"
                @change="updateSetValues(exercise.id, set.id, set)"
                class="value-input"
              />
            </div>
            <div class="cell">
              <input 
                type="number" 
                v-model="set.reps"
                @change="updateSetValues(exercise.id, set.id, set)"
                class="value-input"
              />
            </div>
            <div class="cell">
              <input 
                type="number" 
                v-model="set.time"
                @change="updateSetValues(exercise.id, set.id, set)"
                class="value-input"
              />
            </div>
            <div class="cell">
              <input
                type="checkbox"
                v-model="set.completed"
                @change="updateSet(exercise.id, set.id, set.completed)"
              />
            </div>
            <div class="cell">
              <button 
                @click="removeSet(exercise, set.id)" 
                class="delete-button"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
        <!-- Add Set Button -->
        <div class="add-set-button-container">
          <button 
            @click="addSet(exercise)" 
            class="secondary-button"
          >
            Add Set
          </button>
        </div>
      </div>
    </section>
    <p v-else>No exercises found for this workout.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { API_BASE_URL } from "../config";
import { useRoute, useRouter } from "vue-router";

const workout = ref({
  name: '',
  description: '',
  start_time: null,
  end_time: null,
  exercises: [],
});
const workoutId = ref(null);
const route = useRoute();
const router = useRouter();
const profileId = localStorage.getItem("selectedProfileId");
const token = localStorage.getItem("token");

const addSet = (exercise) => {
  const newSet = {
    reps: 0,
    weight: 0,
    time: 0,
    completed: false
  };
  exercise.sets.push(newSet);
};

const removeSet = async (exercise, setId) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/profiles/${profileId}/workouts/${workoutId.value}/exercises/${exercise.id}/sets/${setId}`,
      {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to delete set");
    }
    
    // Update local state by removing the set
    exercise.sets = exercise.sets.filter(set => set.id !== setId);
  } catch (error) {
    console.error("Error deleting set:", error);
  }
};

// Instructions modal state
const showInstructions = ref(false);
const currentInstructions = ref('');

const showInstructionsFor = (exercise) => {
  if (exercise.exercise?.instructions) {
    currentInstructions.value = exercise.exercise.instructions.join('\n\n');
  } else {
    currentInstructions.value = 'No instructions available.';
  }
  showInstructions.value = true;
};

const closeInstructions = () => {
  showInstructions.value = false;
  currentInstructions.value = '';
};

// Fetch the workout details
const fetchWorkout = async () => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/profiles/${profileId}/workouts/${workoutId.value}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      }
    );

    if (!response.ok) {
      throw new Error("Failed to fetch workout");
    }

    const data = await response.json();
    console.log('Workout data:', data); // Debug log
    workout.value = data;
  } catch (error) {
    console.error("Error fetching workout:", error);
  }
};

// Update the set completion status
const updateSet = async (exerciseId, setId, completed) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/profiles/${profileId}/workouts/${workoutId.value}/exercises/${exerciseId}/sets/${setId}`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ completed }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to update set");
    }
  } catch (error) {
    console.error("Error updating set:", error);
  }
};

// Update set values (weight, reps, time)
const updateSetValues = async (exerciseId, setId, set) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/profiles/${profileId}/workouts/${workoutId.value}/exercises/${exerciseId}/sets/${setId}`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          weight: Number(set.weight),
          reps: Number(set.reps),
          time: Number(set.time),
          completed: set.completed
        }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to update set values");
    }
  } catch (error) {
    console.error("Error updating set values:", error);
  }
};

// Format time (seconds to mm:ss)
const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${minutes}:${secs < 10 ? "0" : ""}${secs}`;
};

// End the workout
const endWorkout = async () => {
  try {
    const currentTime = new Date();
    const formattedTime = currentTime.toTimeString().split(' ')[0]; // This will give "HH:MM:SS"
    
    const response = await fetch(
      `${API_BASE_URL}/api/profiles/${profileId}/workouts/${workoutId.value}`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ end_time: formattedTime }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to end workout");
    }

    router.push('/workouts');
  } catch (error) {
    console.error("Error ending workout:", error);
  }
};

onMounted(() => {
  workoutId.value = route.params.id;
  fetchWorkout();
});
</script>

<style scoped>
.workout-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.workout-header {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: var(--menu-bar-color);
  border-radius: 8px;
}

.workout-header h1 {
  font-size: 2rem;
  margin-bottom: 1rem;
  color: var(--text-color);
}

.workout-header p {
  margin: 0.5rem 0;
  color: var(--text-color);
}

.end-button {
  background-color: #dc3545;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.end-button:hover {
  background-color: #c82333;
}

.exercise-block {
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  background-color: var(--menu-bar-color);
  border-radius: 8px;
}

.exercise-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.exercise-header h3 {
  margin: 0;
  color: var(--text-color);
}

.instructions-button {
  padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.instructions-button:hover {
  background-color: #0056b3;
}

.sets-table {
  width: 100%;
  border-radius: 4px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 0.5fr 1fr 1fr 1fr 0.5fr;
  background-color: rgba(255, 255, 255, 0.1);
  padding: 0.75rem;
  gap: 0.5rem;
}

.header-cell {
  color: var(--text-color);
  font-weight: bold;
  text-align: center;
}

.table-row {
  display: grid;
  grid-template-columns: 0.5fr 1fr 1fr 1fr 0.5fr;
  padding: 0.75rem;
  gap: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.cell {
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-color);
}

.value-input {
  width: 80px;
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--text-color);
  text-align: center;
}

.value-input:focus {
  outline: none;
  border-color: #007bff;
}

/* Instructions Modal */
.instructions-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.instructions-content {
  background-color: var(--menu-bar-color);
  width: 90%;
  max-width: 500px;
  border-radius: 8px;
  overflow: hidden;
}

.instructions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.instructions-header h3 {
  margin: 0;
  color: var(--text-color);
}

.close-button {
  background: none;
  border: none;
  color: var(--text-color);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
}

.instructions-body {
  padding: 1rem;
  color: var(--text-color);
}

@media (max-width: 768px) {
  .workout-page {
    padding: 1rem;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .header-cell {
    text-align: left;
  }
  
  .cell {
    justify-content: flex-start;
  }
  
  .value-input {
    width: 100%;
  }
}

.table-header, .table-row {
  display: grid;
  grid-template-columns: 0.5fr 1fr 1fr 1fr 0.5fr 0.5fr;
  padding: 0.75rem;
  gap: 0.5rem;
}

.add-set-button-container {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
}

.secondary-button {
  background-color: #4CAF50;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.secondary-button:hover {
  background-color: #45a049;
}

.delete-button {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.3rem 0.6rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.3s;
}

.delete-button:hover {
  background-color: #c82333;
}

@media (max-width: 768px) {
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .cell {
    justify-content: space-between;
    display: flex;
  }
  
  .header-cell {
    display: none;
  }
  
  .cell::before {
    content: attr(data-label);
    font-weight: bold;
  }
}
</style>