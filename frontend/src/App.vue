<template class="bg-white dark:bg-gray-900">
  <nav class="fixed w-full border border-gray-200 bg-blue-100 dark:bg-gray-800 z-10 top-0">
    <div class="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
      <router-link to="/" exact class="flex items-center space-x-3 rtl:space-x-reverse">
        <img 
         v-if="isDarkMode"
         @click="redirectToHome"
          class="h-16 w-56 cursor-pointer transition-colors duration-300"
          src="./assets/MoveIt-logo(dark).png"
          alt="MoveIt Logo"

        />
        <img 
        v-else
        @click="redirectToHome"
          class="h-16 w-32 cursor-pointer transition-colors duration-300"
          src="./assets/MoveIt-logo1.png"
          alt="MoveIt Logo"
        />
      </router-link>

      <div class="flex md:order-2 space-x-3 md:space-x-0 rtl:space-x-reverse">
        <!-- Dark mode toggle button -->
        <button @click="toggleDarkMode" class="text-gray-800 p-2 rounded dark:text-white">
          <span class="sr-only">Toggle Dark Mode</span>
          <i v-if="isDarkMode" class="fas fa-sun text-yellow-500"></i>
          <i v-else class="fas fa-moon text-blue-800"></i>
        </button>
      </div>
      <div class="items-center justify-between hidden w-full md:flex md:w-auto md:order-1" id="navbar-cta">
        <ul class="flex flex-col font-medium p-4 md:p-0 mt-4 rounded-lg md:space-x-8 rtl:space-x-reverse md:flex-row md:mt-0 md:border-0 bg-blue-100 dark:bg-gray-800">
          <router-link
            to="/"
            exact
            class="w-40 text-center block shadow-md border-2 rounded-lg py-2 px-3 md:p-4 text-[#003f88] bg-blue-700 border-[#003f88] md:bg-transparent md:text-[#003f88] dark:text-white dark:border-white dark:bg-transparent"
            :class="{ 'active-link ': $route.path === '/' }"
          >
            Home
          </router-link>
          <router-link
            to="/Shipments"
            class="w-40 text-center block shadow-md border-2 rounded-lg py-2 px-3 md:p-4 text-[#003f88] bg-blue-700 border-[#003f88] md:bg-transparent md:text-[#003f88] dark:text-white dark:border-white dark:bg-transparent"
            :class="{ 'active-link ': $route.path === '/Shipments' }"
          >
            Shipments
          </router-link>
          <router-link
            to="/AllShipments"
            class="w-40 text-center block shadow-md border-2 rounded-lg py-2 px-3 md:p-4 text-[#003f88] bg-blue-700 border-[#003f88] md:bg-transparent md:text-[#003f88] dark:text-white dark:border-white dark:bg-transparent"
            :class="{ 'active-link ': $route.path === '/AllShipments' }"
          >
            All Shipments
          </router-link>
          <router-link
            to="/logicalroutes"
            class="w-40 text-center block shadow-md border-2 rounded-lg py-2 px-3 md:p-4 text-[#003f88] bg-blue-700 border-[#003f88] md:bg-transparent md:text-[#003f88] dark:text-white dark:border-white dark:bg-transparent"
            :class="{ 'active-link ': $route.path === '/logicalroutes' }"
          >
            Logical Routes
          </router-link>
        </ul>
      </div>
    </div>
  </nav>

  <div class="mt-24 relative bg-white dark:bg-gray-900 min-h-screen">
    <keep-alive > 
      <router-view></router-view>
    </keep-alive>

  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const isDarkMode = ref(false);
const router = useRouter();

// Toggle dark mode
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value;
  const body = document.body;

  // Toggle dark class
  if (isDarkMode.value) {
    body.classList.add('dark');
  } else {
    body.classList.remove('dark');
  }
};

const redirectToHome = () => {
  router.push('/');
};
</script>

<style scoped>
.active-link {
  @apply text-yellow-500 dark:text-yellow-500;
}
</style>
