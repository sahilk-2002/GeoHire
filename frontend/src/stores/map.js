import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMapStore = defineStore('map', () => {
  const center = ref([20, 0])
  const zoom = ref(2)
  const selectedJob = ref(null)

  function setCenter(lat, lng) {
    if (typeof lat === 'object') {
      const obj = lat
      center.value = [obj.lat ?? obj[0] ?? 20, obj.lng ?? obj[1] ?? 0]
    } else {
      center.value = [lat, lng ?? 0]
    }
    zoom.value = 11
  }

  function selectJob(job) {
    selectedJob.value = job
  }

  function clearSelection() {
    selectedJob.value = null
  }

  return { center, zoom, selectedJob, setCenter, selectJob, clearSelection }
})
