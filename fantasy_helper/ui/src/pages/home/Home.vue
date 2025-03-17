<script setup>
import { useLeaguesInfoStore } from '@/stores/leaguesInfo.store'
import { onMounted } from 'vue'
import { ref } from 'vue'

const message_1 = ref('Hello World 1!')
console.log('Create message 1')

const leaguesInfoStore = useLeaguesInfoStore()

const message_2 = ref('Hello World 2!')
console.log('Create message 2')

onMounted(async () => {
  console.log('Mounted hook triggered') // Test basic log
  // throw new Error('Test error') // Force error
  // try {
  await leaguesInfoStore.fetchLeaguesInfo()
  // } catch (error) {
  //   // Handle UI-specific errors
  //   console.error(error)
  //   // const message = ref('Hello World!')
  // }
})

const message_3 = ref('Hello World 3!')
console.log('Create message 3')

</script>

<template>
  <h1>{{ message_1 }}</h1>
  <h1>{{ message_2 }}</h1>
  <h1>{{ message_3 }}</h1>

  <div v-if="leaguesInfoStore.leagues.length">
    <h2>Leagues:</h2>
    <ul>
      <li v-for="league in leaguesInfoStore.leagues" :key="league.name">
        {{ league.ru_name }}
      </li>
    </ul>
  </div>

</template>
