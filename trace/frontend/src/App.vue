<template>
  <div class="min-h-screen bg-gray-900 text-white">
    <!-- Top Header -->
    <header class="fixed top-0 left-0 w-full h-16 bg-gray-900 z-50 flex items-center px-4 shadow">
      <h1 class="text-xl font-bold">Your App</h1>
    </header>

    <!-- Sidebar -->
    <SidebarNavigation />

    <!-- Main Content -->
    <main class="pt-16 pl-0 sm:pl-64 min-h-screen bg-gray-900">
      <div class="p-4">
        <MainContent />
      </div>
    </main>
  </div>
</template>
<script setup>
import { onMounted } from 'vue'
import { initFlowbite } from 'flowbite'
import SidebarNavigation from './components/SidebarNavigation.vue'
import MainContent from './components/MainContent.vue'

onMounted(() => {
  initFlowbite()
})
</script>
