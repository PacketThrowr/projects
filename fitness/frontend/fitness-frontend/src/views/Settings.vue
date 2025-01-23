<template>
  <div class="settings-container">
    <!-- Sidebar -->
    <aside class="sidebar">
      <nav class="sidebar-nav">
        <button 
          @click="activeSection = 'general'"
          :class="{ active: activeSection === 'general' }"
          class="nav-item"
        >
          General
        </button>
        
        <!-- Admin Section with sub-items -->
        <div v-if="isSuperUser" class="nav-group">
          <button 
            @click="toggleAdminMenu"
            :class="{ active: activeSection.startsWith('admin') }"
            class="nav-item with-arrow"
          >
            <span>Admin</span>
            <span :class="['arrow', { 'arrow-down': !showAdminMenu, 'arrow-up': showAdminMenu }]">▼</span>
          </button>
          <!-- Admin sub-items -->
          <div v-if="showAdminMenu" class="nav-subitems">
            <button 
              @click="selectSubSection('admin-users')"
              :class="{ active: activeSection === 'admin-users' }"
              class="nav-subitem"
            >
              User Management
            </button>
          </div>
        </div>
      </nav>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- General Section -->
      <div v-if="activeSection === 'general'" class="content-section">
        <h2>General Settings</h2>
        <div class="settings-items">
          <div class="settings-item">
            <span>Theme</span>
            <ThemeToggle />
          </div>
        </div>
      </div>

      <!-- Admin - User Management Section -->
      <div v-if="activeSection === 'admin-users'" class="content-section">
        <UserManagement v-if="isSuperUser" />
      </div>
    </main>
  </div>
</template>

<script setup>
import ThemeToggle from "../components/ThemeToggle.vue";
import UserManagement from "../views/UserManagement.vue";
import { ref, onMounted } from 'vue';
import { API_BASE_URL } from "../config";

const isSuperUser = ref(false);
const activeSection = ref('general');
const showAdminMenu = ref(false);

const toggleAdminMenu = () => {
  showAdminMenu.value = !showAdminMenu.value;
};

const selectSubSection = (section) => {
  activeSection.value = section;
};

onMounted(async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) throw new Error('Failed to fetch user data');
    const userData = await response.json();
    isSuperUser.value = userData.is_superuser;
  } catch (error) {
    console.error('Error fetching user data:', error);
  }
});
</script>

<style scoped>
.settings-container {
  display: flex;
  position: fixed;
  top: 48px; /* Match your menu bar height */
  left: 0;
  right: 0;
  bottom: 0;
  background-color: var(--background-color);
}

.sidebar {
  width: 180px;
  background-color: var(--menu-bar-color);
  height: calc(100vh - 48px); /* Subtract menu bar height */
  position: fixed;
  left: 0;
  top: 48px; /* Match your menu bar height */
  bottom: 0;
  padding-top: 1rem;
}

.main-content {
  flex: 1;
  margin-left: 180px;
  padding: 2rem;
  overflow-y: auto;
  height: calc(100vh - 48px);
}

.nav-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.5rem;
  text-align: left;
  color: var(--menu-bar-text-color);
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
}

.nav-item:hover,
.nav-subitem:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  background-color: rgba(255, 255, 255, 0.15);
}

.nav-item .arrow {
  font-size: 0.8rem;
  transition: transform 0.2s;
}

.nav-item .arrow-up {
  transform: rotate(180deg);
}

.nav-subitems {
  background-color: rgba(0, 0, 0, 0.2);
}

.nav-subitem {
  padding: 0.75rem 2.5rem;
  text-align: left;
  color: var(--menu-bar-text-color);
  cursor: pointer;
  border: none;
  background: none;
  width: 100%;
}

.nav-subitem.active {
  background-color: rgba(255, 255, 255, 0.15);
}

.content-section {
  height: 100%;
}

.settings-items {
  background-color: var(--menu-bar-color);
  border-radius: 8px;
  overflow: hidden;
}

.settings-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--background-color);
}

.settings-item:last-child {
  border-bottom: none;
}

.settings-item span {
  color: var(--menu-bar-text-color);
}
</style>