<template>
  <div class="workout-page">
    <!-- Header -->
    <header class="workout-header">
      <h1>{{ workout.name }}</h1>
      <p>{{ workout.description }}</p>
      <p>
        <strong>Start Time:</strong> {{ workout.start_time || "Not started yet" }}
      </p>
      <button @click="endWorkout" class="end-button">End Workout</button>
    </header>

    <!-- Exercises Section -->
    <section v-if="workout.exercises && workout.exercises.length > 0" class="exercises-section">
      <h2>Exercises</h2>
      <div v-for="exercise in workout.exercises" :key="exercise.id" class="exercise-block">
        <h3>Exercise ID: {{ exercise.exercise_id }}</h3>
        <div class="sets">
          <div class="set" v-for="(set, index) in exercise.sets" :key="set.id">
            <div>
              <p>Reps: {{ set.reps }}</p>
              <p>Weight: {{ set.weight }}</p>
              <p>Time: {{ formatTime(set.time) }}</p>
            </div>
            <label>
              <input
                type="checkbox"
                v-model="set.completed"
                @change="updateSet(exercise.id, set.id, set.completed)"
              />
              Completed
            </label>
          </div>
        </div>
      </div>
    </section>
    <p v-else>No exercises found for this workout.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { API_BASE_URL } from "../config";
import { useRoute } from "vue-router";

const workout = ref({
  name: '',
  description: '',
  start_time: null,
  end_time: null,
  exercises: [], // Initialize with an empty array to avoid null errors when iterating
});
const workoutId = ref(null); // Extracted from route params
const route = useRoute();
const profileId = localStorage.getItem("selectedProfileId");
const token = localStorage.getItem("token");

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

    workout.value = await response.json();
    console.log("Fetched workout:", workout.value);
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

    console.log(`Set ${setId} updated successfully.`);
  } catch (error) {
    console.error("Error updating set:", error);
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
    const response = await fetch(
      `${API_BASE_URL}/api/profiles/${profileId}/workouts/${workoutId.value}`,
      {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ end_time: new Date().toISOString() }),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to end workout");
    }

    console.log("Workout ended.");
    // Redirect to the workout list page
    window.location.href = "/workouts";
  } catch (error) {
    console.error("Error ending workout:", error);
  }
};

// Fetch workout details on page load
onMounted(() => {
  workoutId.value = route.params.id;
  fetchWorkout();
});
</script>

<style scoped>
.workout-page {
  padding: 2rem;
  background-color: var(--menu-bar-color);
  color: var(--text-color);
}

.workout-header {
  margin-bottom: 2rem;
}

.workout-header h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.workout-header p {
  margin: 0.5rem 0;
}

.end-button {
  background-color: #dc3545;
  color: white;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}

.end-button:hover {
  background-color: #c82333;
}

.exercises-section {
  margin-top: 2rem;
}

.exercise-block {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.set {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}
</style>
