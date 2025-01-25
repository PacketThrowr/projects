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
                <div class="exercise-header">
                  <h4>{{ exercise.exercise.name }}</h4>
                    <div>
                      <button type="button" @click="addSet(exercise)" class="secondary-button">Add Set</button>
                      <button type="button" @click="removeExercise(exercise)" class="delete-button">Delete Exercise</button>
                    </div>
                  <button type="button" @click="addSet(exercise)" class="secondary-button">Add Set</button>
                </div>
                
                <div class="sets-table">
                  <div class="set-header" :class="{'time-layout': exercise.exercise.recorded_type === 'TIME'}">
                    <span>#</span>
                    <span v-if="exercise.exercise.recorded_type === 'REPS'">Reps</span>
                    <span v-if="exercise.exercise.recorded_type === 'REPS'">Weight</span>
                    <span v-if="exercise.exercise.recorded_type === 'TIME'">Time (mm:ss)</span>
                    <span>Complete</span>
                  </div>

                  <div v-for="(set, index) in exercise.sets" :key="index" class="set-row" :class="{'time-layout': exercise.exercise.recorded_type === 'TIME'}">
                    <span>{{ index + 1 }}</span>
                    <template v-if="exercise.exercise.recorded_type === 'REPS'">
                      <input type="number" v-model="set.reps" min="0">
                      <input type="number" v-model="set.weight" min="0">
                    </template>
                    <template v-if="exercise.exercise.recorded_type === 'TIME'">
                      <div class="time-input">
                        <input type="number" v-model="set.minutes" min="0" placeholder="mm">
                        <input type="number" v-model="set.seconds" min="0" max="59" placeholder="ss">
                      </div>
                    </template>
                    <input type="checkbox" v-model="set.completed">
                    <!-- Delete button for sets -->
                    <button @click="removeSet(exercise, index)" class="delete-button">Delete</button>
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
        <div v-else class="modal-body exercise-selection">
          <!-- Modal Actions at the Top -->
          <div class="top-actions">
            <button @click="hideExerciseSelection" class="cancel-button">Back</button>
            <button @click="confirmExerciseSelection" class="submit-button">Add Selected</button>
          </div>

          <!-- Search Bar -->
          <div class="search-bar">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Search exercises..."
              class="search-input"
            >
          </div>
          
          <!-- Exercise Filters -->
          <ExerciseFilters 
            :exercises="exercises"
            @filter-change="handleFilterChange"
          />

          <!-- Exercises Grid -->
          <div class="exercises-grid">
            <div 
              v-for="exercise in filteredExercises" 
              :key="exercise.id" 
              class="exercise-card" 
              :class="{ selected: isExerciseSelected(exercise) }"
            >
              <div class="exercise-image" @click="toggleExercise(exercise)">
                <img :src="exercise.picture || '/placeholder.jpg'" alt="">
              </div>
              <div class="exercise-info" @click="toggleExercise(exercise)">
                <div class="info-row">
                  <h3>{{ exercise.name }}</h3>
                  <div class="info-icon" @click.stop="showInstructions(exercise)">i</div>
                </div>
                <p v-if="exercise.muscle_category">{{ exercise.muscle_category }}</p>
              </div>
            </div>
          </div>
        </div>
      <div v-if="activeInstructions" class="modal-overlay" @click="hideInstructions">
        <div class="instruction-modal" @click.stop>
          <h3>Instructions</h3>
          <ul>
            <li v-for="(instruction, index) in activeInstructions" :key="index">
              {{ instruction }}
            </li>
          </ul>
          <button @click="hideInstructions" class="close-button">×</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineEmits } from 'vue';
import { API_BASE_URL } from '../config';
import ExerciseFilters from './ExerciseFilters.vue';

const editMode = ref(false);
const showModal = ref(false);
const isExerciseSelection = ref(false);
const exercises = ref([]);
const emits = defineEmits(['workoutUpdated']);
const filters = ref({
  exerciseCategory: '',
  exerciseEquipment: '',
  primaryMuscles: ''
});
const filteredExercises = ref([]);
const formData = ref({
  name: '',
  description: '',
  profile_id: 1, // You'll need to get this from your user profile
  exercises: []
});

const removeSet = (exercise, index) => {
  exercise.sets.splice(index, 1);
};

const selectedExercises = ref([]);
const handleFilterChange = (filters) => {
  filteredExercises.value = exercises.value.filter(exercise => {
    const categoryMatch = !filters.category || exercise.category === filters.category;
    const equipmentMatch = !filters.equipment || exercise.equipment === filters.equipment;
    const muscleMatch = !filters.muscle || 
      exercise.primaryMuscles.includes(filters.muscle) || 
      exercise.secondaryMuscles.includes(filters.muscle);
    
    return categoryMatch && equipmentMatch && muscleMatch;
  });
};

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
        recorded_type: exercise.recorded_type,
        weight_type: exercise.weight_type,
      },
      exercise_id: exercise.id,
      sets: []
    };
    console.log('New exercise:', newExercise);  // Add this line
    selectedExercises.value.push(newExercise);
  }
};

const removeExercise = async (exercise) => {
  // Confirm deletion (optional)
  if (!confirm(`Are you sure you want to delete the exercise: ${exercise.exercise.name}?`)) {
    return;
  }

  // Remove from selected exercises array
  selectedExercises.value = selectedExercises.value.filter((e) => e.id !== exercise.id);

  // If the exercise is already saved in the backend, make an API call to delete it
  if (editMode.value && exercise.id) {
    try {
      const profileId = localStorage.getItem('selectedProfileId');
      const token = localStorage.getItem('token');
      const workoutPlanId = formData.value.id;

      const response = await fetch(
        `${API_BASE_URL}/api/profiles/${profileId}/workout_plans/${workoutPlanId}/exercises/${exercise.id}/`,
        {
          method: 'DELETE',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error('Failed to delete exercise');
      }

      console.log(`Exercise ${exercise.id} deleted successfully.`);
    } catch (error) {
      console.error('Error deleting exercise:', error);
    }
  }
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
        exercise_id: exercise.exercise_id,
        sets: exercise.sets.map(set => ({
          reps: set.reps || 0,
          weight: set.weight || 0,
          time: set.time || 0,
          completed: set.completed || false,
        }))
      }))
    };

    console.log('Submitting workoutData:', workoutData);

    const method = editMode.value ? 'PUT' : 'POST';
    const workoutId = editMode.value ? formData.value.id : '';
    const url = editMode.value
      ? `${API_BASE_URL}/api/profiles/${profileId}/workout_plans/${workoutId}`
      : `${API_BASE_URL}/api/profiles/${profileId}/workout_plans`;

    const response = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(workoutData),
    });

    if (!response.ok) throw new Error('Failed to save workout');
    const workout = await response.json();

    console.log('Workout saved:', workout);
    emits('workoutUpdated');
    closeModal();
  } catch (error) {
    console.error('Error saving workout:', error);
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

const activeInstructions = ref(null);

const showInstructions = (exercise) => {
  activeInstructions.value = exercise.instructions;
};

const hideInstructions = () => {
  activeInstructions.value = null;
};
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
  padding-bottom: 0; /* Remove padding below the header */
  margin-bottom: 0;
}

.modal-body {
  padding: 1rem;
  overflow-y: auto;
  padding-top: 0;
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

.modal-header .close-button {
 background: #dc3545;
 color: white;
 padding: 8px 16px;
 border: none;
 border-radius: 4px;
 display: flex;
 align-items: center;
 gap: 8px;
}

.modal-header .close-button::after {
 content: 'Close';
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

.info-row {
 display: flex;
 align-items: center;
 gap: 8px;
}

.info-icon {
 width: 20px;
 height: 20px;
 border-radius: 50%;
 background: rgba(255, 255, 255, 0.2);
 display: flex;
 align-items: center;
 justify-content: center;
 cursor: pointer;
 font-size: 12px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  z-index: 1050;
  display: flex;
  align-items: center;
  justify-content: center;
}

.instruction-modal {
  background: var(--menu-bar-color);
  padding: 20px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.instruction-modal .close-button {
 background: #dc3545;
 color: white;
 padding: 8px 16px;
 border: none;
 border-radius: 4px;
 display: flex;
 align-items: center;
 gap: 8px;
 margin-top: 16px;
}

.close-button::after {
 content: 'Close';
}

.delete-button {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.3s;
}

.delete-button:hover {
  background-color: #c82333;
}

.top-actions {
  position: sticky;
  top: 0;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  background-color: var(--menu-bar-color);
  z-index: 10;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1); /* Optional: Adds a separator line */
  margin-top: 0; /* Remove any margin above the buttons */
  padding-top: 0.5rem;
}

.exercise-header .delete-button {
  margin-left: 10px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: background-color 0.3s;
}

.exercise-header .delete-button:hover {
  background-color: #c82333;
}
</style>