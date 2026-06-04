import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useJobsStore = defineStore('jobs', () => {
  const jobs = ref([])
  const matches = ref([])
  const location = ref('')
  const loading = ref(false)
  const error = ref('')

  async function fetchJobs(loc) {
    loading.value = true
    error.value = ''
    location.value = loc
    try {
      const res = await fetch(`/api/jobs?location=${encodeURIComponent(loc)}`)
      const data = await res.json()
      jobs.value = data.jobs || []
    } catch {
      jobs.value = []
      error.value = 'Backend unreachable. Start the API server or add mock data.'
    } finally {
      loading.value = false
    }
  }

  async function scrapeJobs(loc) {
    loading.value = true
    error.value = ''
    try {
      const res = await fetch(`/api/scrape?location=${encodeURIComponent(loc)}`, { method: 'POST' })
      const data = await res.json()
      jobs.value = data.jobs || []
    } catch {
      error.value = 'Could not load jobs. Start the backend server.'
    } finally {
      loading.value = false
    }
  }

  async function matchJobs(resumeId, loc) {
    loading.value = true
    error.value = ''
    try {
      const res = await fetch(`/api/match-jobs?resume_id=${encodeURIComponent(resumeId)}&location=${encodeURIComponent(loc)}`, { method: 'POST' })
      const data = await res.json()
      matches.value = data.matches || []
    } catch {
      matches.value = []
      error.value = 'Matching failed. Backend may be offline.'
    } finally {
      loading.value = false
    }
  }

  function loadMockData() {
    jobs.value = [
      { id: '1', title: 'Senior UX Designer', company: 'Stripe', location: 'San Francisco, CA', description: 'Lead design for our core payments platform.', requirements: ['5+ years UX design', 'Figma expertise', 'Design systems'], salary: '$140k – $180k', job_type: 'Full-time', source: 'mock', latitude: 37.7749, longitude: -122.4194 },
      { id: '2', title: 'Full Stack Developer', company: 'Airbnb', location: 'New York, NY', description: 'Build features for our host platform.', requirements: ['React', 'Node.js', 'PostgreSQL'], salary: '$160k – $210k', job_type: 'Remote', source: 'mock', latitude: 40.7128, longitude: -74.0060 },
      { id: '3', title: 'Product Manager', company: 'Google', location: 'Mountain View, CA', description: 'Drive strategy for core search products.', requirements: ['5+ years PM', 'Technical background', 'Analytics'], salary: '$180k – $240k', job_type: 'Full-time', source: 'mock', latitude: 37.3861, longitude: -122.0839 },
      { id: '4', title: 'Frontend Engineer', company: 'Framer', location: 'Amsterdam, NL', description: 'Build world-class design tools.', requirements: ['TypeScript', 'React', 'Canvas API'], salary: '$90k – $120k', job_type: 'Contract', source: 'mock', latitude: 52.3676, longitude: 4.9041 },
      { id: '5', title: 'Data Scientist', company: 'Spotify', location: 'New York, NY', description: 'Improve music recommendation algorithms.', requirements: ['Python', 'ML', 'TensorFlow'], salary: '$170k – $220k', job_type: 'Full-time', source: 'mock', latitude: 40.7580, longitude: -73.9855 },
    ]
    error.value = ''
  }

  return { jobs, matches, location, loading, error, fetchJobs, scrapeJobs, matchJobs, loadMockData }
})
