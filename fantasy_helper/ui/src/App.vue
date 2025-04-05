<script>
import AppHeader from './components/AppHeader.vue'

export default {
  name: 'App', 
  components: { 
    AppHeader
  },
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
  <div class="min-h-screen bg-gray-50">
    <AppHeader />
    <main class="py-8">
      <router-view />
    </main>
  </div>
</template>

<style>
html, body {
  background-color: #90e3ba!important;
}

/* Add proper layout */
#app {
  @apply min-h-screen flex flex-col;
}

main {
  @apply flex-1;
}
</style>
