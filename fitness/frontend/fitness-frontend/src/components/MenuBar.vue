<template>
  <nav class="menu-bar">
    <!-- Left-aligned menu items -->
    <ul class="menu-items">
      <li><router-link to="/dashboard">Dashboard</router-link></li>
      <li><router-link to="/workouts">Workouts</router-link></li>
      <li><router-link to="/cardio-sessions">Cardio Sessions</router-link></li>
      <li class="menu-dropdown">
        <button @click="toggleAccountMenu" class="dropdown-button">
          Account
          <span :class="{ 'arrow-up': showAccountMenu, 'arrow-down': !showAccountMenu }">▼</span>
        </button>
        <div v-if="showAccountMenu" class="dropdown-content">
          <router-link to="/user" class="menu-item">User</router-link>
          <router-link to="/profiles" class="menu-item">Profiles</router-link>
          <router-link to="/settings" class="menu-item">Settings</router-link>
          <button @click="logout" class="menu-item logout-button">Logout</button>
        </div>
      </li>
    </ul>

    <!-- Right-aligned items -->
    <div class="right-menu">
      <!-- Profile Selector -->
      <div class="profile-selector menu-dropdown">
        <span class="profile-label">Profile:</span>
        <button @click="toggleProfileMenu" class="dropdown-button">
          {{ currentProfile ? currentProfile.name : 'Select Profile' }}
          <span :class="{ 'arrow-up': showProfileMenu, 'arrow-down': !showProfileMenu }">▼</span>
        </button>
        <div v-if="showProfileMenu" class="dropdown-content">
          <button 
            v-for="profile in profiles" 
            :key="profile.id"
            @click="selectProfile(profile)"
            class="menu-item"
          >
            {{ profile.name }}
          </button>
        </div>
      </div>
      
      <!-- Theme toggle -->
      <div class="theme-toggle-container">
        <ThemeToggle />
      </div>
    </div>
  </nav>
</template>

<script>
import ThemeToggle from "./ThemeToggle.vue";
import { API_BASE_URL } from "../config";

export default {
  components: {
    ThemeToggle,
  },
  data() {
    return {
      showAccountMenu: false,
      showProfileMenu: false,
      profiles: [],
      currentProfile: null
    };
  },
  methods: {
    toggleAccountMenu() {
      this.showAccountMenu = !this.showAccountMenu;
    },
    toggleProfileMenu() {
      this.showProfileMenu = !this.showProfileMenu;
    },
    async fetchProfiles() {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE_URL}/api/profiles/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        if (!response.ok) throw new Error('Failed to fetch profiles');
        this.profiles = await response.json();
        
        // Load previously selected profile from localStorage
        const savedProfileId = localStorage.getItem('selectedProfileId');
        if (savedProfileId) {
          const savedProfile = this.profiles.find(p => p.id === parseInt(savedProfileId));
          if (savedProfile) {
            this.selectProfile(savedProfile);
          }
        } else if (this.profiles.length > 0) {
          // Select first profile by default
          this.selectProfile(this.profiles[0]);
        }
      } catch (error) {
        console.error('Error fetching profiles:', error);
      }
    },
    selectProfile(profile) {
      this.currentProfile = profile;
      localStorage.setItem('selectedProfileId', profile.id);
      this.showProfileMenu = false;
      // Emit event for other components to react to profile change
      this.$emit('profile-changed', profile);
    },
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("selectedProfileId");
      this.$router.push("/");
    },
    handleClickOutside(event) {
      if (!event.target.closest('.menu-dropdown')) {
        this.showAccountMenu = false;
        this.showProfileMenu = false;
      }
    }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
    this.fetchProfiles();
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  }
};
</script>

<style scoped>
.menu-bar {
  position: fixed;
  width: 100%;
  left: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background-color: var(--menu-bar-color);
  color: var(--menu-bar-text-color);
  z-index: 1000;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  bottom: 0;
}

@media (min-width: 768px) {
  .menu-bar {
    top: 0;
    bottom: auto;
  }
}

.menu-items {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 1rem;
}

.menu-items li {
  margin: 0;
}

.menu-items a {
  color: var(--menu-bar-text-color);
  text-decoration: none;
  font-weight: 500;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.menu-items a:hover {
  text-decoration: none;
  background-color: rgba(255, 255, 255, 0.1);
}

.menu-items a.router-link-active {
  background-color: rgba(255, 255, 255, 0.15);
}

.theme-toggle-container {
  display: flex;
  align-items: center;
  max-width: fit-content;
}

.menu-dropdown {
  position: relative;
}

.dropdown-button {
  background: none;
  border: none;
  color: var(--menu-bar-text-color);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0.5rem 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.dropdown-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.arrow-up, .arrow-down {
  font-size: 0.8rem;
  transition: transform 0.2s;
}

.arrow-up {
  transform: rotate(180deg);
}

.dropdown-content {
  position: absolute;
  right: 0;
  top: 100%;
  background-color: var(--menu-bar-color);
  min-width: 160px;
  box-shadow: 0 8px 16px rgba(0,0,0,0.2);
  border-radius: 4px;
  padding: 0.5rem 0;
  z-index: 1000;
  margin-top: 0.5rem;
}

.menu-item {
  display: block;
  padding: 0.75rem 1rem;
  text-decoration: none;
  color: var(--menu-bar-text-color);
  text-align: left;
  width: 100%;
  border: none;
  background: none;
  font: inherit;
  cursor: pointer;
  transition: background-color 0.2s;
  box-sizing: border-box;
  margin: 0;
}

.menu-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.menu-item.router-link-active {
  background-color: rgba(255, 255, 255, 0.15);
}

.logout-button {
  color: #ff4444;
  width: 100%;
  box-sizing: border-box;
}

.logout-button:hover {
  background-color: rgba(255, 0, 0, 0.1);
}

.right-menu {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.profile-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.profile-label {
  color: var(--menu-bar-text-color);
  font-weight: 500;
}

.dropdown-content .menu-item.active {
  background-color: rgba(255, 255, 255, 0.15);
}
</style>