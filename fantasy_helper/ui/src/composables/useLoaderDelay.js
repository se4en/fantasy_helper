import { ref, watch, onUnmounted } from 'vue'

export function useLoaderDelay(isLoadingRef, delay = 500) {
  const showLoader = ref(false)
  let timeoutId = null
  let startTime = 0

  watch(isLoadingRef, (loading) => {
    if (loading) {
      // Loading starts
      startTime = Date.now()
      showLoader.value = true
      if (timeoutId) clearTimeout(timeoutId)
    } else {
      // Loading ends - calculate remaining time
      const elapsed = Date.now() - startTime
      const remaining = delay - elapsed
      
      if (remaining > 0) {
        timeoutId = setTimeout(() => {
          showLoader.value = false
        }, remaining)
      } else {
        showLoader.value = false
      }
    }
  })

  onUnmounted(() => {
    if (timeoutId) clearTimeout(timeoutId)
  })

  return { showLoader }
}
