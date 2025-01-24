<template>
  <div v-if="showModal" class="modal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ editMode ? 'Edit Workout' : 'Add Workout' }}</h2>
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
              <div v-for="exercise in selectedExercises" :key="exercise.id" class="exercise-block">
                {{ console.log('Rendering exercise:', exercise) }}
                <div class="exercise-header">
                  <h4>{{ exercise.exercise.name }}</h4>
                  <button type="button" @click="addSet(exercise)" class="secondary-button">Add Set</button>
                </div>
                
                <div class="sets-table">
                  <div class="set-header" :class="{'time-layout': exercise.exercise.measurement_type === 'TIME'}">
                    <span>#</span>
                    <span v-if="exercise.exercise.measurement_type === 'REPS'">Reps</span>
                    <span v-if="exercise.exercise.measurement_type === 'REPS'">Weight</span>
                    <span v-if="exercise.exercise.measurement_type === 'TIME'">Time (mm:ss)</span>
                    <span>Complete</span>
                  </div>

                  <div v-for="(set, index) in exercise.sets" :key="index" class="set-row" :class="{'time-layout': exercise.exercise.measurement_type === 'TIME'}">
                    <span>{{ index + 1 }}</span>
                    <template v-if="exercise.exercise.measurement_type === 'REPS'">
                      <input type="number" v-model="set.reps" min="0">
                      <input type="number" v-model="set.weight" min="0">
                    </template>
                    <template v-if="exercise.exercise.measurement_type === 'TIME'">
                      <div class="time-input">...</div>
                    </template>
                    <input type="checkbox" v-model="set.completed">
                  </div>
                </div>
              </div>
            </div>
            <button type="button" @click="showExerciseSelection" class="secondary-button">
              Add Exercises
            </button>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeModal" class="cancel-button">Cancel</button>
            <button type="submit" class="submit-button">
              {{ editMode ? 'Update' : 'Create' }} Workout
            </button>
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

const editMode = ref(false);
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

const addSet = (exercise, e) => {
  e?.preventDefault();  // Add this line to prevent any default behavior
  if (!exercise.sets) exercise.sets = [];
  
  const newSet = {
    reps: 0,
    weight: 0,
    time: 0,
    completed: false,
    minutes: 0,
    seconds: 0
  };
  
  exercise.sets.push(newSet);
};

const updateSeconds = (set) => {
  set.time = (parseInt(set.minutes) * 60) + parseInt(set.seconds);
};

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
    const data = await response.json();
    console.log('Fetched exercises:', data); // Add this line to inspect the data
    exercises.value = data;
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
  console.log('Original exercise:', exercise);  // Add this line
  if (isExerciseSelected(exercise)) {
    selectedExercises.value = selectedExercises.value.filter(e => e.id !== exercise.id);
  } else {
    const newExercise = {
      ...exercise,
      exercise: {
        id: exercise.id,
        name: exercise.name,
        measurement_type: exercise.measurement_type,
        weight_type: exercise.weight_type,
      },
      exercise_id: exercise.id,
      sets: []
    };
    console.log('New exercise:', newExercise);  // Add this line
    selectedExercises.value.push(newExercise);
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
    const token = localStorage.getItem('token');

    const workoutData = {
      name: formData.value.name,
      description: formData.value.description,
      profile_id: parseInt(profileId),
      exercises: selectedExercises.value.map(exercise => ({
        exercise_id: exercise.id,
        sets: exercise.sets.map(set => ({
          reps: set.reps || 0,  // Default to 0 instead of null
          weight: set.weight || 0, 
          time: exercise.weight_type === 'TIME' ? (set.time || 0) : null,
          completed: set.completed || false
        }))
      }))
    };

    // Use PUT for edit, POST for create
    const method = editMode.value ? 'PUT' : 'POST';
    const workoutId = editMode.value ? formData.value.id : '';
    const url = editMode.value 
      ? `${API_BASE_URL}/api/profiles/${profileId}/workout_plans/${workoutId}`
      : `${API_BASE_URL}/api/profiles/${profileId}/workout_plans`;

    const workoutResponse = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(workoutData)
    });

    if (!workoutResponse.ok) {
      const error = await workoutResponse.json();
      console.error('Workout operation error:', error);
      throw new Error(`Failed to ${editMode.value ? 'update' : 'create'} workout`);
    }

    const workout = await workoutResponse.json();

    if (editMode.value) {
      // Delete existing exercises
      const existingExercises = await fetch(
        `${API_BASE_URL}/api/profiles/${profileId}/workout_plans/${workoutId}/exercises`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      );
      const exercises = await existingExercises.json();
      
      for (const exercise of exercises) {
        await fetch(
          `${API_BASE_URL}/api/profiles/${profileId}/workout_plans/${workoutId}/exercises/${exercise.id}`,
          {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
          }
        );
      }
    }

    // Add exercises 
    for (const exercise of selectedExercises.value) {
      await fetch(`${API_BASE_URL}/api/profiles/${profileId}/workout_plans/${workout.id}/exercises`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ exercise_id: exercise.id })
      });
    }

    // Get exercises with IDs
    const exercisesResponse = await fetch(
      `${API_BASE_URL}/api/profiles/${profileId}/workout_plans/${workout.id}/exercises`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    const exercises = await exercisesResponse.json();

    // Add sets using returned exercise IDs
    for (const [index, exercise] of exercises.entries()) {
      const sets = selectedExercises.value[index].sets || [];
      for (const set of sets) {
        await fetch(
          `${API_BASE_URL}/api/profiles/${profileId}/workout_plans/${workout.id}/exercises/${exercise.id}/sets`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              completed: set.completed,
              weight: set.weight || 0,
              reps: set.reps || 0,
              time: set.time || 0
            })
          }
        );
      }
    }

    closeModal();
  } catch (error) {
    console.error('Error:', error);
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

const initializeEditForm = (plan) => {
  editMode.value = true;
  formData.value = {
    id: plan.id,  // Important to add this
    name: plan.name,
    description: plan.description,
    profile_id: plan.profile_id,
  };
  selectedExercises.value = plan.exercises || [];
};

defineExpose({ showModal, closeModal, editMode, initializeEditForm });
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

.exercise-block {
  width: 100%;
  margin-bottom: 1rem;
  background: var(--background-color);
  padding: 1rem;
  border-radius: 4px;
}

.exercise-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.sets-table {
  width: 100%;
}

.set-header, .set-row {
  display: grid;
  grid-template-columns: 40px repeat(2, 1fr) 80px;
  gap: 1rem;
  align-items: center;
  padding: 0.5rem 0;
}

.time-input {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.time-input input {
  width: 60px;
}

.set-row {
  display: grid;
  grid-template-columns: 40px repeat(2, 1fr) 80px;
  gap: 1rem;
  align-items: center;
  padding: 0.5rem 0;
}

.set-row.time-layout {
  grid-template-columns: 40px 1fr 80px;
}

.set-header {
  display: grid;
  grid-template-columns: 40px repeat(2, 1fr) 80px;
  gap: 1rem;
  align-items: center;
  padding: 0.5rem 0;
}

.set-header.time-layout {
  grid-template-columns: 40px 1fr 80px;
}
</style>