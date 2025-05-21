<template>
  <aside
    id="logo-sidebar"
    class="fixed top-0 left-0 z-40 w-64 h-screen pt-20 transition-transform bg-white border-r border-gray-200 sm:translate-x-0 dark:bg-gray-800 dark:border-gray-700"
    :class="{ '-translate-x-full': !isSidebarOpen, 'translate-x-0': isSidebarOpen }"
  >
    <div class="h-full px-3 pb-4 overflow-y-auto">
      <fwb-sidebar class="space-y-1">
        <!-- Dashboard -->
        <fwb-sidebar-item>
          <template #icon>
            <div class="w-5 h-5 flex items-center justify-center">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 22 21">
                <path d="M16.975 11H10V4.025..." />
                <path d="M12.5 0c-.157 0-.311.01..." />
              </svg>
            </div>
          </template>
          <template #default>Dashboard</template>
        </fwb-sidebar-item>

        <!-- Kanban -->
        <fwb-sidebar-item>
          <template #icon>
            <div class="w-5 h-5 flex items-center justify-center">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 18 18">
                <path d="M6.143 0H1.857A1.857..." />
              </svg>
            </div>
          </template>
          <template #default>Kanban</template>
          <template #suffix>
            <span class="ml-2 px-2 text-xs font-semibold bg-gray-100 text-gray-800 rounded-full dark:bg-gray-700 dark:text-gray-300">
              Pro
            </span>
          </template>
        </fwb-sidebar-item>

        <!-- Inbox -->
        <fwb-sidebar-item>
          <template #icon>
            <div class="w-5 h-5 flex items-center justify-center">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2.003 5.884L10 9.882..." />
              </svg>
            </div>
          </template>
          <template #default>Inbox</template>
          <template #suffix>
            <span class="ml-2 w-6 h-6 text-xs flex items-center justify-center font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
              3
            </span>
          </template>
        </fwb-sidebar-item>

        <!-- Dropdown -->
        <fwb-sidebar-dropdown-item>
          <template #icon>
            <div class="w-5 h-5 flex items-center justify-center">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 0C4.485 0 0 4.485..." />
              </svg>
            </div>
          </template>
          <template #trigger>
            E-commerce
          </template>
          <template #default>
            <fwb-sidebar-item class="pl-11">Products</fwb-sidebar-item>
            <fwb-sidebar-item class="pl-11">Sign In</fwb-sidebar-item>
            <fwb-sidebar-item class="pl-11">Sign Up</fwb-sidebar-item>
          </template>
        </fwb-sidebar-dropdown-item>
      </fwb-sidebar>
    </div>
  </aside>

  <!-- Mobile Button -->
  <button
    @click="toggleSidebar"
    data-drawer-target="logo-sidebar"
    data-drawer-toggle="logo-sidebar"
    aria-controls="logo-sidebar"
    type="button"
    class="inline-flex items-center p-2 mt-2 ml-3 text-sm text-gray-500 rounded-lg sm:hidden hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:text-gray-400 dark:hover:bg-gray-700 dark:focus:ring-gray-600"
  >
    <span class="sr-only">Open sidebar</span>
    <svg
      class="w-6 h-6"
      fill="currentColor"
      viewBox="0 0 20 20"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        clip-rule="evenodd"
        fill-rule="evenodd"
        d="M2 4.75A.75.75 0 012.75 4h14.5a..."
      ></path>
    </svg>
  </button>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  FwbSidebar,
  FwbSidebarItem,
  FwbSidebarDropdownItem,
} from 'flowbite-vue'

const isSidebarOpen = ref(window.innerWidth >= 640)

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

onMounted(() => {
  window.addEventListener('resize', () => {
    if (window.innerWidth >= 640) {
      isSidebarOpen.value = true
    }
  })
})
</script>
