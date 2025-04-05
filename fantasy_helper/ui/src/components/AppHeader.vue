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
  <div class="wrapper">
    <nav class="navbar">
      <div class="container">
        <!-- <div class="logo">
          <router-link :to="{ name: 'Home' }">
            <img src="/your-logo.png" alt="Logo" class="navbar-logo" />
          </router-link>
        </div>
         -->
        <ul class="nav-links">
          <li>
            <router-link :to="{ name: 'Home' }" class="nav-link">
              Home
            </router-link>
          </li>
          
          <li v-for="route in availableRoutes" :key="route.name">
            <router-link :to="{ name: route.name }" class="nav-link">
              {{ route.meta?.label || route.name }}
            </router-link>
          </li>
          
          <li>
            <router-link :to="{ name: 'Login' }" class="nav-link">
              Login
            </router-link>
          </li>
        </ul>
      </div>
    </nav>
  </div>
</template>

<style scoped>
/* CSS Reset specifically for navigation elements */
*, *::before, *::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
  border: 0;
}

/* Your existing styles with some modifications */
.wrapper {
  width: 100vw; /* Use viewport width to ensure full width */
  margin: 0;
  padding: 0;
  overflow-x: hidden; /* Prevent horizontal scrollbar */
  border: 0;
  border-width: 0;
  outline: none;
}

.navbar {
  background-color: rgba(0, 0, 0, 0.8);
  position: sticky;
  top: 0;
  z-index: 2100;
  width: 100%;
  margin: 0;
  padding: 0;
  border: 0 !important;
  border-width: 0 !important;
  outline: none;
  box-shadow: none !important;
}

.container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  margin: 0;
  padding: 0;
  height: 60px;
  border: 0 !important;
  border-width: 0 !important;
}

.nav-links {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 20px;
  border: 0;
}

.nav-links li {
  margin: 0;
  padding: 0;
  border: 0;
}

.nav-link {
  color: white; /* Change text color to white */
  font-weight: 700; /* Make text bold (700 is bold) */
  text-decoration: none;
  padding: 8px 12px;
  transition: all 0.2s ease; /* Transition all changing properties */
  border: 0;
  outline: none;
  position: relative; /* For positioning the underline indicator */
}

/* Hover effect - you can adjust this color as needed */
.nav-link:hover {
  color: #f0ad4e; /* Golden color on hover */
}

/* Active/current page styling */
.nav-link.router-link-exact-active,
.nav-link.router-link-active {
  color: #f0ad4e; /* Highlight color for active page */
  font-weight: 800; /* Even bolder for active page */
}

/* Add overrides for any potential framework styles */
nav, div, ul, li, a {
  border: 0 !important;
  border-width: 0 !important;
  border-style: none !important;
  outline: none !important;
  box-shadow: none !important;
}
</style>
