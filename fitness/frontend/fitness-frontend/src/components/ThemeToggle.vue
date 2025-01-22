<template>
  <button @click="toggleTheme" class="theme-toggle">
    {{ isDarkTheme ? "Switch to Light Mode" : "Switch to Dark Mode" }}
  </button>
</template>

<script>
import { ref } from "vue";

export default {
  name: "ThemeToggle",
  setup() {
    const isDarkTheme = ref(false);

    // Set the theme on initial load
    const currentTheme = localStorage.getItem("theme") || "light";
    document.documentElement.classList.toggle("dark", currentTheme === "dark");
    isDarkTheme.value = currentTheme === "dark";

    // Function to toggle the theme
    const toggleTheme = () => {
      isDarkTheme.value = !isDarkTheme.value;
      const newTheme = isDarkTheme.value ? "dark" : "light";
      document.documentElement.classList.toggle("dark", isDarkTheme.value);
      localStorage.setItem("theme", newTheme); // Save theme preference
    };

    return { isDarkTheme, toggleTheme };
  },
};
</script>

<style scoped>
.theme-toggle {
  padding: 0.5rem 1rem;
  background-color: var(--menu-bar-color);
  color: var(--menu-bar-text-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
}

.theme-toggle:hover {
  opacity: 0.8;
}
</style>
