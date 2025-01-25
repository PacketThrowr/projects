<template>
  <div class="workouts-page">
    <!-- Header Section -->
    <div class="header">
      <h1>Workouts</h1>
      <button @click="openAddWorkoutModal" class="add-button">Add Workout Program</button>
    </div>

    <!-- Workout Plans Section -->
    <section class="workouts-section">
      <h2>Workout Plans</h2>
      <div class="plans-wrapper">
        <button 
          class="scroll-button left" 
          @click="scrollLeft"
          :class="{ 'visible': canScrollLeft }"
        >
          &#8592;
        </button>
        <div class="plans-container" ref="plansContainer">
          <div 
            v-for="plan in workoutPlans" 
            :key="plan.id" 
            class="plan-tile"
          >
            <div class="menu-button">
              <button @click.stop="toggleMenu(plan.id)" class="dots-button">⋮</button>
              <div v-if="menuStates[plan.id]" class="menu">
                <button @click="startWorkout(plan)">Start Workout</button>
                <button @click="editWorkout(plan)">Edit</button>
                <button @click="showDeleteConfirmationModal(plan.id)">Delete</button>
              </div>
            </div>
            <h3>{{ plan.name }}</h3>
            <p>{{ plan.description }}</p>
            <p class="exercise-count">Exercises: {{ plan.exercises.length }}</p>
          </div>
        </div>
        <button 
          class="scroll-button right" 
          @click="scrollRight"
          :class="{ 'visible': canScrollRight }"
        >
          &#8594;
        </button>
      </div>
    </section>

    <!-- Previous Workouts Section -->
    <section class="workouts-section">
      <h2>Previous Workouts</h2>
      <div class="workouts-container">
        <!-- Content for previous workouts will go here -->
      </div>
    </section>

    <!-- All Workouts Section -->
    <section class="workouts-section">
      <h2>All Workouts</h2>
      <div class="workouts-container">
        <!-- Content for all workouts will go here -->
      </div>
    </section>

    <!-- Add Workout Modal -->
    <AddWorkoutModal ref="addWorkoutModal" @workoutUpdated="fetchWorkoutPlans" />

    <!-- Confirmation Modal -->
    <div v-if="showDeleteConfirmation" class="confirmation-modal">
      <div class="confirmation-content">
        <p>Are you sure you want to delete this workout plan?</p>
        <div class="confirmation-actions">
          <button @click="confirmDeleteWorkout" class="confirm-button">Yes, Delete</button>
          <button @click="cancelDelete" class="cancel-button">Cancel</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import AddWorkoutModal from '../components/AddWorkoutModal.vue';
import { API_BASE_URL } from '../config';

const addWorkoutModal = ref(null);
const workoutPlans = ref([]);
const plansContainer = ref(null);
const canScrollLeft = ref(false);
const canScrollRight = ref(false);
const menuStates = ref({});

const showDeleteConfirmation = ref(false);
const workoutPlanToDelete = ref(null);

const startWorkout = async (plan) => {
  try {
    const token = localStorage.getItem("token");
    const profileId = localStorage.getItem("selectedProfileId");
    const today = new Date().toISOString().split('T')[0];

    // Create workout
    const workoutResponse = await fetch(
      `${API_BASE_URL}/api/profiles/${profileId}/workouts/`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: plan.name,
          description: plan.description,
          profile_id: parseInt(profileId),
          date: today,
          start_time: null,
          end_time: null,
        })
      }
    );

    if (!workoutResponse.ok) throw new Error("Failed to create workout");
    const workout = await workoutResponse.json();

    // Add exercises and their sets
    for (const planExercise of plan.exercises) {
      // Create exercise
      const exerciseResponse = await fetch(
        `${API_BASE_URL}/api/profiles/${profileId}/workouts/${workout.id}/exercises/`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            exercise_name: planExercise.exercise.name
          })
        }
      );

      if (!exerciseResponse.ok) throw new Error("Failed to create exercise");
      
      // Get exercise ID from workout_exercises of this workout
      const getExercisesResponse = await fetch(
        `${API_BASE_URL}/api/profiles/${profileId}/workouts/${workout.id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          }
        }
      );

      const workoutDetails = await getExercisesResponse.json();
      if (!workoutDetails.exercises || workoutDetails.exercises.length === 0) {
        throw new Error("No exercises found for this workout.");
      }
      const workoutExercise = workoutDetails.exercises[workoutDetails.exercises.length - 1];
      if (!workoutExercise.id) {
        throw new Error("Exercise ID not found in workout details.");
      }

      // Create sets with the proper exercise ID
      for (const set of planExercise.sets) {
        const setResponse = await fetch(
          `${API_BASE_URL}/api/profiles/${profileId}/workouts/${workout.id}/exercises/${workoutExercise.id}/sets/`,
          {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              completed: false,
              weight: set.weight,
              reps: set.reps,
              time: set.time || 0
            })
          }
        );
        
        if (!setResponse.ok) {
          const error = await setResponse.text();
          throw new Error("Failed to create set: " + error);
        }
      }
    }

    window.location.href = `/workout/${workout.id}`;
  } catch (error) {
    console.error("Error starting workout:", error);
  }
};

const editWorkout = (plan) => {
 addWorkoutModal.value.showModal = true;
 addWorkoutModal.value.editMode = true;
 addWorkoutModal.value.initializeEditForm(plan);
};

const toggleMenu = (planId) => {
  menuStates.value[planId] = !menuStates.value[planId];
};

const openAddWorkoutModal = () => {
  addWorkoutModal.value.showModal = true;
};

const fetchWorkoutPlans = async () => {
  try {
    const profileId = localStorage.getItem('selectedProfileId');
    if (!profileId) {
      throw new Error('No profile selected');
    }
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/api/profiles/${profileId}/workout_plans`,{
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    workoutPlans.value = await response.json();
  } catch (error) {
    console.error('Error fetching workout plans:', error);
  }
};

const showDeleteConfirmationModal = (id) => {
  workoutPlanToDelete.value = id;
  showDeleteConfirmation.value = true;
};

const confirmDeleteWorkout = async () => {
  if (!workoutPlanToDelete.value) return;

  try {
    const profileId = localStorage.getItem('selectedProfileId');
    const token = localStorage.getItem('token');
    await fetch(`${API_BASE_URL}/api/profiles/${profileId}/workout_plans/${workoutPlanToDelete.value}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      }
    });
    fetchWorkoutPlans();
  } catch (error) {
    console.error('Error deleting workout:', error);
  } finally {
    cancelDelete();
  }
};

const cancelDelete = () => {
  workoutPlanToDelete.value = null;
  showDeleteConfirmation.value = false;
};

const checkScroll = () => {
  if (plansContainer.value) {
    const { scrollLeft, scrollWidth, clientWidth } = plansContainer.value;
    canScrollLeft.value = scrollLeft > 0;
    canScrollRight.value = scrollLeft < scrollWidth - clientWidth;
  }
};

const scrollLeft = () => {
  if (plansContainer.value) {
    plansContainer.value.scrollBy({ left: -300, behavior: 'smooth' });
  }
};

const scrollRight = () => {
  if (plansContainer.value) {
    plansContainer.value.scrollBy({ left: 300, behavior: 'smooth' });
  }
};

onMounted(() => {
  fetchWorkoutPlans();
  checkScroll();
  window.addEventListener('resize', checkScroll);
  if (plansContainer.value) {
    plansContainer.value.addEventListener('scroll', checkScroll);
  };
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.menu-button')) {
      menuStates.value = {};
    }
  });
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkScroll);
  if (plansContainer.value) {
    plansContainer.value.removeEventListener('scroll', checkScroll);
  };
  document.removeEventListener('click');
});
</script>

<style scoped>
#app {
  width: 100%;
  min-width: fit-content;
  overflow-x: auto;
}

html, body {
  margin: 0;
  padding: 0;
  overflow-x: hidden; /* Prevent horizontal scrolling */
  width: 100%; /* Ensure the page doesn't exceed the viewport width */
  box-sizing: border-box; /* Include padding in width calculations */
}

.workouts-page {
  width: 100%;
  padding: 0 2rem;
  box-sizing: border-box;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

h1 {
  color: var(--text-color);
  margin: 0;
  font-size: 2rem;
}

.add-button {
  padding: 0.5rem 1rem;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.add-button:hover {
  background-color: #45a049;
}

.workouts-section {
  width: 100%;
  margin-bottom: 3rem;
  position: relative;
  background-color: var(--menu-bar-color);
}
h2 {
  color: var(--text-color);
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.workouts-container {
  display: flex;
  overflow-x: auto;
  gap: 1rem;
  padding: 1rem;
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
  width: 100%;
}

/* Add this if you want to hide the scrollbar but keep functionality */
.workouts-container::-webkit-scrollbar {
  display: none;
}

.plans-wrapper {
  position: relative;
  padding: 1rem;
}

.plans-container {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  scroll-behavior: smooth;
  scrollbar-width: none;
  width: 100%;
  padding: 0 2rem;
}

.plans-container::-webkit-scrollbar {
  display: none;
}

.plan-tile {
  flex: 0 0 300px;
  background-color: #1a1a1a;
  padding: 2rem;
  border-radius: 8px; /* Match the parent's border-radius */
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
  height: 200px;

  /* Flexbox for centering content */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden; /* Prevent content overflow */
}

.plan-tile h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.plan-tile p {
  margin: 0.5rem 0;
}

.exercise-count {
  position: absolute;
  bottom: 1rem;
  left: 0;
  right: 0;
  text-align: center;
  font-weight: 500;
  color: var(--text-color);
  font-size: 1rem; /* Optional: Adjust font size for better alignment */
}

.plan-tile h3 {
  margin: 0;
  font-size: 1.5rem;
  color: var(--text-color);
  font-weight: 600;
}

.plan-tile p {
  margin: 0;
  color: var(--text-color);
  opacity: 0.8;
}

.exercise-count {
  margin-top: auto;
  font-weight: 500;
  color: var(--text-color);
}

.scroll-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  padding: 0.5rem;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.3s;
  z-index: 1;
}

.scroll-button.visible {
  opacity: 1;
}

.scroll-button.left {
  left: 1rem;
}

.scroll-button.right {
  right: 1rem;
}

.scroll-button:hover {
  background-color: rgba(0, 0, 0, 0.7);
}

@media (max-width: 480px) {
 .plan-tile {
   width: calc(100% - 2rem);
   min-width: unset;
   flex: 0 0 auto;
 }
 
 .plans-container {
   padding: 0 1rem;
 }


}
.workouts-section h2 {
  padding: 0 1rem;
}

.menu-button {
 position: absolute;
 top: 1rem;
 right: 1rem;
}

.dots-button {
 background: none;
 border: none;
 color: var(--text-color);
 font-size: 1.5rem;
 cursor: pointer;
 padding: 0.25rem;
}

.menu {
 position: absolute;
 right: 0;
 top: 100%;
 background: #1a1a1a;
 border: 1px solid rgba(255, 255, 255, 0.1);
 border-radius: 4px;
 padding: 0.5rem;
 z-index: 10;
}

.menu button {
 display: block;
 width: 100%;
 padding: 0.5rem 1rem;
 text-align: left;
 background: none;
 border: none;
 color: var(--text-color);
 cursor: pointer;
}

.menu button:hover {
 background: rgba(255, 255, 255, 0.1);
}
</style>