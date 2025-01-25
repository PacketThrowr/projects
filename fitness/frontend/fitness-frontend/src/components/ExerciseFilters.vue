<template>
  <div class="filter-container">
    <div class="filters">
      <div class="filter-group">
        <h3 class="filter-header">Category</h3>
        <select v-model="selectedCategory" class="filter-select" @change="emitChanges">
          <option value="">All Categories</option>
          <option v-for="category in availableCategories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <h3 class="filter-header">Equipment</h3>
        <select v-model="selectedEquipment" class="filter-select" @change="emitChanges">
          <option value="">All Equipment</option>
          <option v-for="item in availableEquipment" :key="item" :value="item">
            {{ item }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <h3 class="filter-header">Muscles</h3>
        <select v-model="selectedMuscle" class="filter-select" @change="emitChanges">
          <option value="">All Muscles</option>
          <option v-for="muscle in availableMuscles" :key="muscle" :value="muscle">
            {{ muscle }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <h3 class="filter-header">Force</h3>
        <select v-model="selectedForce" class="filter-select" @change="emitChanges">
          <option value="">All Forces</option>
          <option v-for="force in availableForces" :key="force" :value="force">
            {{ force }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';

const props = defineProps({
  exercises: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['filter-change']);

const selectedCategory = ref('');
const selectedEquipment = ref('');
const selectedMuscle = ref('');
const selectedForce = ref('');

const categories = computed(() => [...new Set(props.exercises.map(ex => ex.category))]);

const filteredExercises = computed(() => {
 return props.exercises.filter(ex => {
   const categoryMatch = !selectedCategory.value || ex.category === selectedCategory.value;
   const equipmentMatch = !selectedEquipment.value || ex.equipment === selectedEquipment.value;
   const muscleMatch = !selectedMuscle.value || 
     ex.primaryMuscles.includes(selectedMuscle.value) || 
     ex.secondaryMuscles.includes(selectedMuscle.value);
   return categoryMatch && equipmentMatch && muscleMatch;
 });
});

const availableCategories = computed(() => {
 let exercises = props.exercises;
 if (selectedEquipment.value) {
   exercises = exercises.filter(ex => ex.equipment === selectedEquipment.value);
 }
 if (selectedMuscle.value) {
   exercises = exercises.filter(ex => 
     ex.primaryMuscles.includes(selectedMuscle.value) || 
     ex.secondaryMuscles.includes(selectedMuscle.value)
   );
 }
 return [...new Set(exercises.map(ex => ex.category))];
});

const availableEquipment = computed(() => {
 let exercises = props.exercises;
 if (selectedCategory.value) {
   exercises = exercises.filter(ex => ex.category === selectedCategory.value);
 }
 if (selectedMuscle.value) {
   exercises = exercises.filter(ex => 
     ex.primaryMuscles.includes(selectedMuscle.value) || 
     ex.secondaryMuscles.includes(selectedMuscle.value)
   );
 }
 return [...new Set(exercises.map(ex => ex.equipment))];
});

const availableMuscles = computed(() => {
 let exercises = props.exercises;
 if (selectedCategory.value) {
   exercises = exercises.filter(ex => ex.category === selectedCategory.value);
 }
 if (selectedEquipment.value) {
   exercises = exercises.filter(ex => ex.equipment === selectedEquipment.value);
 }
 return [...new Set(exercises.flatMap(ex => [...ex.primaryMuscles, ...ex.secondaryMuscles]))];
});

const availableForces = computed(() => {
  let exercises = props.exercises;
  if (selectedCategory.value) exercises = exercises.filter(ex => ex.category === selectedCategory.value);
  if (selectedEquipment.value) exercises = exercises.filter(ex => ex.equipment === selectedEquipment.value);
  if (selectedMuscle.value) exercises = exercises.filter(ex => 
    ex.primaryMuscles.includes(selectedMuscle.value) || ex.secondaryMuscles.includes(selectedMuscle.value));
  return [...new Set(exercises.map(ex => ex.force))];
});

const emitChanges = () => {
  emit('filter-change', {
    category: selectedCategory.value,
    equipment: selectedEquipment.value,
    muscle: selectedMuscle.value,
    force: selectedForce.value
  });
};

watch(selectedCategory, () => {
  // Reset equipment and muscle selections when category changes
  selectedEquipment.value = '';
  selectedMuscle.value = '';
  emitChanges();
});

onMounted(() => {
  emitChanges();
});
</script>

<style scoped>
.filter-container {
  background-color: #1a1a1a;
  padding: 1rem;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.filter-header {
  color: white;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  font-weight: 500;
}

.filter-select {
  width: 100%;
  padding: 0.5rem;
  background-color: #333;
  color: white;
  border: 1px solid #444;
  border-radius: 4px;
}

.filter-select:focus {
  outline: none;
  border-color: #666;
}
</style>
```