import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useMapStore = defineStore('map', () => {
  const center = ref([20, 0])
  const zoom = ref(2)
  const selectedJob = ref(null)

  function setCenter(lat, lon) {
    center.value = [lat, lon]
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
