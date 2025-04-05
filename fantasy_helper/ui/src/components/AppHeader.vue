<script>
  export default {
    computed: {
      availableRoutes() {
        return this.$router.options.routes.filter(route => 
          route.meta?.showInNavigation && 
          !route.meta?.requiresAuth && 
          route.name &&
          route.name !== 'Home' &&
          route.name !== 'Login'
        )
      }
    }
  }
</script>

<template>
  <nav class="bg-white shadow-sm">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between h-16">
        <!-- Left side - Logo/Home -->
        <div class="flex items-center">
          <router-link 
            :to="{ name: 'Home' }" 
            class="text-xl font-bold text-gray-900"
          >
            MyApp
          </router-link>
        </div>

        <!-- Center - Navigation Links -->
        <div class="hidden sm:flex sm:items-center sm:space-x-8 sm:ml-6">
          <router-link
            v-for="route in availableRoutes"
            :key="route.name"
            :to="{ name: route.name }"
            class="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-500 hover:text-gray-700 border-b-2 transition-colors duration-200"
            :class="{
              'border-indigo-500 text-gray-900': $route.name === route.name,
              'border-transparent hover:border-gray-300': $route.name !== route.name
            }"
          >
            {{ route.meta.navTitle }}
          </router-link>
        </div>

        <!-- Right side - Auth/User -->
        <div class="flex items-center">
          <router-link 
            :to="{ name: 'Login' }" 
            class="text-sm font-medium text-gray-500 hover:text-gray-700"
          >
            Login
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>
  
<style scoped>
.router-link-active {
  @apply text-gray-900 border-b-2 border-indigo-500;
}

/* Mobile menu (add if needed later) */
/* @media (max-width: 640px) {
  .sm\:hidden {
    display: none;
  }
} */
</style>