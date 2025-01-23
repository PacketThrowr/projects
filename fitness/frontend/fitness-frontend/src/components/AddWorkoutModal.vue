<template>
  <div v-if="showModal" class="modal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ isExerciseSelection ? 'Select Exercises' : 'Add Workout' }}</h2>
        <button @click="closeModal" class="close-button">&times;</button>
      </div>

      <!-- Workout Form -->
      <div v-if="!isExerciseSelection" class="modal-body">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="name">Name</label>
            <input 
              type="text" 
              id="name" 
              v-model="formData.name" 
              required
            >
          </div>
          
          <div class="form-group">
            <label for="description">Description</label>
            <textarea 
              id="description" 
              v-model="formData.description" 
              rows="3"
            ></textarea>
          </div>

          <div class="form-group">
            <label>Selected Exercises</label>
            <div class="selected-exercises">
              <div v-for="exercise in selectedExercises" :key="exercise.id" class="selected-exercise">
                {{ exercise.name }}
                <button @click.prevent="removeExercise(exercise)" class="remove-button">&times;</button>
              </div>
            </div>
            <button type="button" @click="showExerciseSelection" class="secondary-button">
              Add Exercises
            </button>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="cancel-button">Cancel</button>
            <button type="submit" class="submit-button">Create Workout</button>
          </div>
        </form>
        </div>

      <!-- Exercise Selection -->
      <div v-else class="modal-body">
        <!-- Add search bar above the filters -->
        <div class="search-bar">
            <input 
            type="text" 
            v-model="searchQuery" 
            placeholder="Search exercises..."
            class="search-input"
            >
        </div>
        <div class="filters">
          <div class="filter-group">
            <label>Weight Type</label>
            <select v-model="filters.weightType">
              <option value="">All</option>
              <option value="OTHER">Other</option>
              <!-- Add other weight types -->
            </select>
          </div>

          <div class="filter-group">
            <label>Muscle Category</label>
            <select v-model="filters.muscleCategory">
              <option value="">All</option>
              <option value="Legs">Legs</option>
              <!-- Add other categories -->
            </select>
          </div>

          <div class="filter-group">
            <label>Muscle Groups</label>
            <select v-model="filters.muscleGroups">
              <option value="">All</option>
              <option value="Quads">Quads</option>
              <!-- Add other muscle groups -->
            </select>
          </div>
        </div>

        <div class="exercises-grid">
          <div 
            v-for="exercise in filteredExercises" 
            :key="exercise.id"
            class="exercise-card"
            :class="{ selected: isExerciseSelected(exercise) }"
            @click="toggleExercise(exercise)"
          >
            <div class="exercise-image">
              <img :src="exercise.picture || '/placeholder.jpg'" alt="">
            </div>
            <div class="exercise-info">
              <h3>{{ exercise.name }}</h3>
              <p v-if="exercise.muscle_category">{{ exercise.muscle_category }}</p>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button @click="hideExerciseSelection" class="cancel-button">Back</button>
          <button @click="confirmExerciseSelection" class="submit-button">Add Selected</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { API_BASE_URL } from '../config';

const showModal = ref(false);
const isExerciseSelection = ref(false);
const exercises = ref([]);
const selectedExercises = ref([]);
const filters = ref({
  weightType: '',
  muscleCategory: '',
  muscleGroups: ''
});

const formData = ref({
  name: '',
  description: '',
  profile_id: 1, // You'll need to get this from your user profile
  exercises: []
});

// Fetch exercises
const fetchExercises = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/exercises`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) throw new Error('Failed to fetch exercises');
    exercises.value = await response.json();
  } catch (error) {
    console.error('Error fetching exercises:', error);
  }
};

const searchQuery = ref('');

// Update the filteredExercises computed property
const filteredExercises = computed(() => {
  return exercises.value.filter(exercise => {
    // First check the search query
    if (searchQuery.value && !exercise.name.toLowerCase().includes(searchQuery.value.toLowerCase())) {
      return false;
    }
    
    // Then check the other filters
    if (filters.value.weightType && exercise.weight_type !== filters.value.weightType) return false;
    if (filters.value.muscleCategory && exercise.muscle_category !== filters.value.muscleCategory) return false;
    if (filters.value.muscleGroups && !exercise.muscle_groups?.includes(filters.value.muscleGroups)) return false;
    return true;
  });
});

const isExerciseSelected = (exercise) => {
  return selectedExercises.value.some(e => e.id === exercise.id);
};

const toggleExercise = (exercise) => {
  if (isExerciseSelected(exercise)) {
    selectedExercises.value = selectedExercises.value.filter(e => e.id !== exercise.id);
  } else {
    selectedExercises.value.push(exercise);
  }
};

const removeExercise = (exercise) => {
  selectedExercises.value = selectedExercises.value.filter(e => e.id !== exercise.id);
};

const showExerciseSelection = () => {
  isExerciseSelection.value = true;
  if (exercises.value.length === 0) {
    fetchExercises();
  }
};

const hideExerciseSelection = () => {
  isExerciseSelection.value = false;
};

const confirmExerciseSelection = () => {
  isExerciseSelection.value = false;
};

const handleSubmit = async () => {
  try {
    const profileId = localStorage.getItem('selectedProfileId');
    if (!profileId) {
      throw new Error('No profile selected');
    }

    const workoutData = {
      ...formData.value,
      profile_id: parseInt(profileId),
      exercises: selectedExercises.value.map(exercise => ({
        id: exercise.id,
        exercise_id: exercise.id,
        workout_id: 0,
        sets: []
      }))
    };

    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/profiles/${profileId}/workout_plans`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(workoutData)
    });

    if (!response.ok) throw new Error('Failed to create workout');
    
    closeModal();
  } catch (error) {
    console.error('Error creating workout:', error);
  }
};

const closeModal = () => {
  showModal.value = false;
  isExerciseSelection.value = false;
  formData.value = {
    name: '',
    description: '',
    profile_id: 1,
    exercises: []
  };
  selectedExercises.value = [];
};

// Expose methods needed by parent
defineExpose({
  showModal,
  closeModal
});
</script>

<style scoped>
.modal {
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

.modal-content {
  background-color: var(--menu-bar-color);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  border-radius: 8px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--background-color);
}

.modal-body {
  padding: 1rem;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

input, textarea, select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  background-color: var(--background-color);
  color: var(--text-color);
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.exercises-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.exercise-card {
  background-color: var(--background-color);
  border-radius: 4px;
  padding: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.exercise-card.selected {
  border: 2px solid #4CAF50;
}

.exercise-image {
  width: 100%;
  height: 150px;
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.exercise-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.exercise-info {
  margin-top: 0.5rem;
}

.exercise-info h3 {
  margin: 0;
  font-size: 1rem;
}

.selected-exercises {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.selected-exercise {
  background-color: var(--background-color);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.remove-button {
  background: none;
  border: none;
  color: var(--text-color);
  cursor: pointer;
  padding: 0;
  font-size: 1.2rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem;
  border-top: 1px solid var(--background-color);
}

.submit-button,
.cancel-button,
.secondary-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.submit-button {
  background-color: #4CAF50;
  color: white;
}

.cancel-button {
  background-color: rgba(255, 255, 255, 0.1);
  color: var(--text-color);
}

.secondary-button {
  background-color: var(--background-color);
  color: var(--text-color);
}

.close-button {
  background: none;
  border: none;
  color: var(--text-color);
  font-size: 1.5rem;
  cursor: pointer;
}
.search-bar {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  background-color: var(--background-color);
  color: var(--text-color);
  font-size: 1rem;
}

.search-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.2);
}
</style>