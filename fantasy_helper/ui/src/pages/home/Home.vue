<script setup>
import { useLeaguesInfoStore } from '@/stores/leaguesInfo.store'
import { storeToRefs } from 'pinia'
import { onMounted } from 'vue'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { useRouter } from 'vue-router'
import Loader from '@/components/Loader.vue'

const leaguesInfoStore = useLeaguesInfoStore()
const router = useRouter()

const { isLoading } = storeToRefs(leaguesInfoStore)
const { showLoader } = useLoaderDelay(isLoading, 500)

const leagueRoute = (league) => {
  return {
    name: 'LeaguePage',
    params: {
      leagueSlug: league.name
    }
  }
}

onMounted(async () => {
  try {
    await leaguesInfoStore.fetchLeaguesInfo()
  } catch (error) {
    console.error(error)
  }
})
</script>

<template>
  <div>
    <h2 class="leagues-header">Available Leagues:</h2>

    <Loader v-if="showLoader" />
    
    <div v-if="!leaguesInfoStore.isLoading">
      <div v-if="leaguesInfoStore.leagues_info.length === 0" class="empty-state">
        No leagues available
      </div>
      <div v-else class="leagues-container">
        <div 
          v-for="(league, index) in leaguesInfoStore.leagues_info" 
          :key="index" 
          class="league-item"
        >
          <router-link 
            :to="leagueRoute(league)"
            class="emoji-link"
          >
            <div class="emoji">{{ league.emoji }}</div>
          </router-link>
          <div class="name">{{ league.ru_name }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-style: italic;
}

.leagues-header {
  text-align: center;
  margin: 2rem 0;
  padding: 0.5rem;
  font-size: 1.8rem;
  color: #2c3e50;
}

.emoji {
  font-size: 2rem;
  transform: scale(1.5); 
  display: inline-block;
  margin-bottom: 0.5rem;
}

.emoji-link {
  transition: transform 0.2s ease;
}

.emoji-link:hover .emoji {
  transform: scale(1.8);
  filter: drop-shadow(0 2px 8px rgba(0, 0, 0, 0.2));
  cursor: pointer;
}

.leagues-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem;
}

.league-item {
  flex: 1 0 23%; /* 4 items per row (100% / 4 - gap) */
  min-width: 200px;
  max-width: calc(25% - 1rem);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  box-sizing: border-box;
}

@media (max-width: 1200px) {
  .league-item {
    flex: 1 0 31%; /* 3 items per row */
    max-width: calc(33.33% - 1rem);
  }
}

@media (max-width: 768px) {
  .league-item {
    flex: 1 0 48%; /* 2 items per row */
    max-width: calc(50% - 1rem);
  }
}

@media (max-width: 480px) {
  .league-item {
    flex: 1 0 100%; /* 1 item per row */
    max-width: 100%;
  }
}
</style>
