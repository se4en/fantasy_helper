<script>
export default {
  data() {
    return {
      features: [
        {
          icon: "📊",
          title: "Advanced Analytics",
          description: "Real-time statistics and performance predictions for players and teams"
        },
        {
          icon: "🤖",
          title: "AI Predictions",
          description: "Machine learning-powered forecasts updated every minute"
        },
        {
          icon: "🏆",
          title: "League Management",
          description: "Track multiple leagues and get personalized recommendations"
        }
      ],
      steps: [
        {
          title: "Connect Your Account",
          description: "Link your fantasy sports platform in seconds"
        },
        {
          title: "Choose Your League",
          description: "Select from supported fantasy leagues"
        },
        {
          title: "Get Smart Insights",
          description: "Receive personalized recommendations and alerts"
        }
      ]
    }
  }
}
</script>

<template>
  <div class="min-h-screen">
    <!-- Hero Section -->
    <section class="text-center py-20 bg-gradient-to-b from-blue-50 to-white">
      <div class="max-w-4xl mx-auto px-4">
        <h1 class="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
          Fantasy Helper
          <span class="text-blue-600">Pro</span>
        </h1>
        <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Your ultimate companion for fantasy sports success. Get real-time insights, 
          expert predictions, and smart team management tools all in one place.
        </p>
        <div class="flex justify-center space-x-4">
          <router-link 
            to="/signup" 
            class="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors text-lg"
          >
            Get Started
          </router-link>
          <router-link 
            to="/features" 
            class="bg-white text-blue-600 px-8 py-3 rounded-lg border-2 border-blue-600 hover:bg-blue-50 transition-colors text-lg"
          >
            Learn More
          </router-link>
        </div>
      </div>
    </section>

    <!-- Key Features -->
    <section class="py-16">
      <div class="max-w-7xl mx-auto px-4 grid md:grid-cols-3 gap-8">
        <div 
          v-for="(feature, index) in features"
          :key="index"
          class="p-6 bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow"
        >
          <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
            <span class="text-2xl">{{ feature.icon }}</span>
          </div>
          <h3 class="text-xl font-semibold mb-2">{{ feature.title }}</h3>
          <p class="text-gray-600">{{ feature.description }}</p>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="bg-gray-50 py-16">
      <div class="max-w-4xl mx-auto px-4 text-center">
        <h2 class="text-3xl font-bold mb-8">How It Works</h2>
        <div class="grid md:grid-cols-3 gap-8">
          <div 
            v-for="(step, index) in steps"
            :key="index"
            class="bg-white p-6 rounded-lg"
          >
            <div class="text-blue-600 text-2xl font-bold mb-2">0{{ index + 1 }}</div>
            <h3 class="text-lg font-semibold mb-2">{{ step.title }}</h3>
            <p class="text-gray-600">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
  
<style scoped>
/* Custom animations */
.hero-enter-active {
  animation: slide-up 0.8s ease;
}

@keyframes slide-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
