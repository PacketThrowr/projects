<template>
  <div class="workouts-page">
    <!-- Header Section -->
    <div class="header">
      <h1>Workouts</h1>
      <button @click="openAddWorkoutModal" class="add-button">Add Workout Program</button>
    </div>

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
    <AddWorkoutModal ref="addWorkoutModal" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import AddWorkoutModal from '../components/AddWorkoutModal.vue';

const addWorkoutModal = ref(null);

const openAddWorkoutModal = () => {
  addWorkoutModal.value.showModal = true;
};
</script>

<style scoped>
.workouts-page {
  padding: 2rem;
  background-color: var(--background-color);
  min-height: 100vh;
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
  margin-bottom: 3rem;
}

h2 {
  color: var(--text-color);
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.workouts-container {
  background-color: var(--menu-bar-color);
  border-radius: 8px;
  padding: 1rem;
  min-height: 100px;
}
</style>