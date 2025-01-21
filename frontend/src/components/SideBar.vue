<template>
    <div class="mt-5" :class="{ 'sidebar-open': sidebarVisible }">
      <div class="left-panel flex items-stretch">
        <div class="fixed h-screen overflow-y-scroll p-4 transition-width duration-300 ease-in-out"
          :class="{ 'w-72': !sidebarVisible, 'w-16 ml-5': sidebarVisible }">
          <div class="flex justify-end p-2">
            <button @click="toggleSidebar" :class="{ 'hamburger-open': !sidebarVisible }"
              class="w-8 h-8 bg-transparent border-none cursor-pointer p-0 z-1">
              <span class="block w-full h-0.5 bg-black mb-2 transition-transform duration-300 transform"
                :class="{ 'rotate-45 -translate-y-0': !sidebarVisible }"></span>
              <span class="block w-full h-0.5 bg-black mb-2 transition-transform duration-300 transform"
                :class="{ 'scale-y-0': !sidebarVisible }"></span>
              <span class="block w-full h-0.5 bg-black mt-2 transition-transform duration-300 transform"
                :class="{ '-rotate-45 -translate-y-5': !sidebarVisible }"></span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { defineProps, defineEmits } from 'vue';
  
  const props = defineProps({
    sidebarVisible: Boolean
  });
  
  const emit = defineEmits(['toggle-sidebar']);
  
  function toggleSidebar() {
    emit('toggle-sidebar');
  }
  </script>
  