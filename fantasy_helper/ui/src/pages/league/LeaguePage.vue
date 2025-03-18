<script setup>
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useLoaderDelay } from '@/composables/useLoaderDelay'
import { onMounted, computed, watch } from 'vue'
import { useLeaguesInfoStore } from '@/stores/leaguesInfo.store'

const route = useRoute()
const router = useRouter()
const leaguesInfoStore = useLeaguesInfoStore()

const { 
  leagues_info,
  isLoading: isLeaguesInfoLoading 
} = storeToRefs(leaguesInfoStore)
const { showLeaguesInfoLoader } = useLoaderDelay(isLeaguesInfoLoading, 500)

const currentLeague = computed(() => {
  return leagues_info.value?.find(league => 
    slugify(league.name) === route.params.leagueSlug
  ) || null
})

const slugify = (str) => {
  return str
    .toLowerCase()
    .replace(/[^\w\s-]/g, '') // Remove special chars
    .replace(/\s+/g, '-')     // Replace spaces with -
    .replace(/--+/g, '-')     // Replace multiple - with single
    .trim()
}

onMounted(async () => {
  try {
    if (!leagues_info.value?.length) {
      await leaguesInfoStore.fetchLeaguesInfo()
    }
  } catch (error) {
    console.error('Failed to load leagues:', error)
    router.replace('/')
  }
})

watch(
  [currentLeague, isLeaguesInfoLoading],
  ([league, loading]) => {
    if (!loading && !league) {
      router.replace('/')
    }
  },
  { immediate: true }
)
</script>

<template>
  <Loader v-if="showLeaguesInfoLoader" />
  
  <div v-else-if="currentLeague">
    <h2 class="league-header">League name: {{ currentLeague.name }}</h2>
  </div>
</template>

<style scoped>
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-style: italic;
}

.league-header {
  text-align: center;
  margin: 2rem 0;
  padding: 0.5rem;
  font-size: 1.8rem;
  color: #2c3e50;
}
</style>
