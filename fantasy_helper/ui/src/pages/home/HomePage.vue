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
  <div class="min-h-screen bg-white">
    <!-- Hero Section -->
    <section class="relative overflow-hidden">
      <div class="max-w-6xl mx-auto px-6 py-24 text-center">
        <div class="space-y-8">
          <h1 class="text-5xl md:text-7xl font-bold text-gray-900 tracking-tight">
            Fantasy Helper
          </h1>
          <p class="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Advanced analytics and AI-powered insights for fantasy sports success. 
            Make smarter decisions with real-time data and expert predictions.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8">
            <router-link 
              to="/leagues" 
              class="bg-gray-900 text-white px-8 py-4 rounded-lg hover:bg-gray-800 transition-all duration-200 text-lg font-medium shadow-sm"
            >
              Browse Leagues
            </router-link>
            <router-link 
              to="/login" 
              class="text-gray-700 px-8 py-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 text-lg font-medium"
            >
              Sign In
            </router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="border-t border-gray-100 py-16">
      <div class="max-w-6xl mx-auto px-6">
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div class="space-y-2">
            <div class="text-3xl font-bold text-gray-900">15+</div>
            <div class="text-sm text-gray-600 uppercase tracking-wide">Leagues</div>
          </div>
          <div class="space-y-2">
            <div class="text-3xl font-bold text-gray-900">1M+</div>
            <div class="text-sm text-gray-600 uppercase tracking-wide">Players Tracked</div>
          </div>
          <div class="space-y-2">
            <div class="text-3xl font-bold text-gray-900">24/7</div>
            <div class="text-sm text-gray-600 uppercase tracking-wide">Live Updates</div>
          </div>
          <div class="space-y-2">
            <div class="text-3xl font-bold text-gray-900">AI</div>
            <div class="text-sm text-gray-600 uppercase tracking-wide">Powered</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-20">
      <div class="max-w-6xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Everything you need to win
          </h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">
            Comprehensive tools and insights to give you the competitive edge in fantasy sports
          </p>
        </div>
        
        <div class="grid md:grid-cols-3 gap-8">
          <div 
            v-for="(feature, index) in features"
            :key="index"
            class="group p-8 rounded-2xl border border-gray-100 hover:border-gray-200 hover:shadow-lg transition-all duration-300"
          >
            <div class="w-14 h-14 bg-gray-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-gray-100 transition-colors">
              <span class="text-2xl">{{ feature.icon }}</span>
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-3">{{ feature.title }}</h3>
            <p class="text-gray-600 leading-relaxed">{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="bg-gray-50 py-20">
      <div class="max-w-4xl mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Get started in minutes
          </h2>
          <p class="text-lg text-gray-600">
            Simple setup process to get you winning faster
          </p>
        </div>
        
        <div class="grid md:grid-cols-3 gap-8">
          <div 
            v-for="(step, index) in steps"
            :key="index"
            class="relative bg-white p-8 rounded-2xl shadow-sm"
          >
            <div class="absolute -top-4 left-8">
              <div class="w-8 h-8 bg-gray-900 text-white rounded-full flex items-center justify-center text-sm font-bold">
                {{ index + 1 }}
              </div>
            </div>
            <h3 class="text-lg font-semibold text-gray-900 mb-3 pt-4">{{ step.title }}</h3>
            <p class="text-gray-600 leading-relaxed">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="py-20">
      <div class="max-w-4xl mx-auto px-6 text-center">
        <div class="bg-gray-900 rounded-3xl p-12 text-white">
          <h2 class="text-3xl md:text-4xl font-bold mb-4">
            Ready to dominate your league?
          </h2>
          <p class="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Join thousands of fantasy managers who are already using Fantasy Helper to win their leagues.
          </p>
          <router-link 
            to="/leagues" 
            class="inline-block bg-white text-gray-900 px-8 py-4 rounded-lg hover:bg-gray-100 transition-colors text-lg font-medium"
          >
            Start Winning Today
          </router-link>
        </div>
      </div>
    </section>
  </div>
</template>
  
<style scoped>
/* Subtle animations and effects */
.group:hover .group-hover\:bg-gray-100 {
  transition: background-color 0.2s ease;
}

/* Custom gradient overlay for hero */
.hero-gradient {
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(0,0,0,0.05) 100%);
}

/* Smooth transitions for all interactive elements */
* {
  transition-property: color, background-color, border-color, transform, box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}
</style>
