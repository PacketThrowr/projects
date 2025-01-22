<template>
  <nav class="menu-bar">
    <!-- Menu items aligned to the left -->
    <ul class="menu-items">
      <li><router-link to="/dashboard">Dashboard</router-link></li>
      <li><router-link to="/profile">Profile</router-link></li>
      <li><router-link to="/settings">Settings</router-link></li>
      <li><a href="#" @click="logout">Logout</a></li>
    </ul>
    <!-- Theme toggle button aligned to the right -->
    <div class="theme-toggle-container">
      <ThemeToggle />
    </div>
  </nav>
</template>

<script>
import ThemeToggle from "./ThemeToggle.vue";

export default {
  components: {
    ThemeToggle,
  },
  methods: {
    logout() {
      localStorage.removeItem("token"); // Clear the token
      this.$router.push("/"); // Redirect to the login page
    },
  },
};
</script>

<style scoped>
/* General menu bar styles */
.menu-bar {
  position: fixed;
  width: 100%; /* Ensure it spans the entire width of the browser */
  left: 0; /* Align the menu bar to the left edge of the screen */
  display: flex;
  justify-content: space-between; /* Space between menu items and theme toggle */
  align-items: center; /* Center items vertically */
  padding: 0.5rem 1rem;
  background-color: var(--menu-bar-color);
  color: var(--menu-bar-text-color);
  z-index: 1000;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* Default: Mobile (menu bar at the bottom) */
.menu-bar {
  bottom: 0; /* Position at the bottom of the screen */
  top: auto;
}

/* Desktop: Menu bar at the top */
@media (min-width: 768px) {
  .menu-bar {
    top: 0; /* Position at the top of the screen */
    bottom: auto; /* Remove bottom alignment */
  }
}

/* Menu items styling */
.menu-items {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 1rem; /* Add spacing between menu items */
}

.menu-items li {
  margin: 0;
}

.menu-items a {
  color: var(--menu-bar-text-color);
  text-decoration: none;
  font-weight: bold;
}

.menu-items a:hover {
  text-decoration: underline;
}

/* Theme toggle container */
.theme-toggle-container {
  display: flex;
  align-items: center; /* Vertically center the button */
  justify-content: flex-end; /* Ensure the button stays at the right */
  flex-grow: 1; /* Allow the button to take up remaining space for alignment */
  max-width: 150px; /* Limit the button's width if needed */
}
</style>
