import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useJobsStore = defineStore('jobs', () => {
  const jobs = ref([])
  const matches = ref([])
  const location = ref('')
  const loading = ref(false)

  async function fetchJobs(loc) {
    loading.value = true
    try {
      const res = await fetch(`/api/jobs?location=${encodeURIComponent(loc)}`)
      jobs.value = await res.json()
    } catch {
      jobs.value = []
    } finally {
      loading.value = false
    }
  }

  async function scrapeJobs(loc) {
    loading.value = true
    try {
      await fetch(`/api/scrape?location=${encodeURIComponent(loc)}`, { method: 'POST' })
      setTimeout(() => fetchJobs(loc), 3000)
    } catch {
      jobs.value = []
    } finally {
      loading.value = false
    }
  }

  async function matchJobs(resumeId, loc) {
    loading.value = true
    try {
      const res = await fetch(`/api/match-jobs?resume_id=${encodeURIComponent(resumeId)}&location=${encodeURIComponent(loc)}`, { method: 'POST' })
      matches.value = await res.json()
    } catch {
      matches.value = []
    } finally {
      loading.value = false
    }
  }

  return { jobs, matches, location, loading, fetchJobs, scrapeJobs, matchJobs }
})
