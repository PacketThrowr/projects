<template>
  <div id="app">
    <!-- Conditionally render the menu bar based on the current route -->
    <MenuBar v-if="showMenuBar" />
    <router-view />
  </div>
</template>

<script>
import { useRoute } from "vue-router";
import MenuBar from "./components/MenuBar.vue";
import { computed } from "vue";

export default {
  name: "App",
  components: {
    MenuBar,
  },
  setup() {
    const route = useRoute();
    const showMenuBar = computed(() => {
      return !["Login", "SignUp"].includes(route.name);
    });

    return {
      showMenuBar,
    };

    return {
      showMenuBar,
    };
  },
};
</script>

<style>
/* Add global styles here if needed */
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background-color: #f7f7f7;
}
</style>
