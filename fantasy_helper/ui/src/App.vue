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
  <div class="wrapper">
    <AppHeader />
    <main class="py-8" style="position: relative;">
      <router-view />
    </main>
  </div>
</template>

<style>
html, body {
  /* background-color: #90e3ba!important; */
  margin: 0;
  padding: 0;
  overflow-x: hidden;
}

body nav,
body .navbar,
body .wrapper,
body .container,
body .nav-links,
body .nav-links li,
body .nav-link {
  border: none !important;
  border-width: 0 !important;
  border-style: none !important;
  margin-top: 0 !important;
  margin-bottom: 0 !important;
  outline: none !important;
  box-shadow: none !important;
}

</style>
