<template>
  <div class="flex shadow-md shadow-gray-800 rounded-lg mb-8 bg-[#2363a3] dark:bg-blue-800 p-8 flex-col">
    <div class="flex items-center mb-3">
      <div class="w-10 h-10 mr-3 inline-flex items-center justify-center rounded-full text-white flex-shrink-0">
        <i class="fa-solid fa-truck-fast"></i>
      </div>
      <h2 class="text-white text-lg font-medium" style="white-space: nowrap;">{{ title }}</h2>
    </div>
    <div class="flex flex-col justify-between flex-grow">
      <div class="leading-relaxed text-4xl text-center text-white h-10 w-10 size-96">
        {{ count }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue';

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  count: {
    type: Number,
    required: true,
  },
});
</script>

<style scoped>
/* Add any custom styling if necessary */
</style>
