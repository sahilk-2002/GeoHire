<template>
  <div class="pb-24 lg:pb-0">
    <header class="bg-background w-full top-0 sticky z-40 transition-all duration-300">
      <div class="flex items-center justify-between px-container-margin lg:px-8 py-sm max-w-7xl mx-auto">
        <div class="flex items-center gap-2 lg:hidden">
          <span class="material-symbols-outlined text-primary">explore</span>
          <h1 class="font-headline-md text-headline-md font-bold text-primary tracking-tight">GeoHire</h1>
        </div>

      </div>
    </header>

    <main class="max-w-7xl mx-auto px-container-margin lg:px-8 pt-4 lg:pt-8">
      <SearchBar @search="handleSearch" />

      <div v-if="jobsStore.error && !jobsStore.jobs.length" class="mb-md p-md bg-error-container text-on-error-container rounded-xl text-sm">
        {{ jobsStore.error }}
      </div>

      <div v-if="jobsStore.jobs.length || jobsStore.matches.length" class="flex items-center justify-between mb-md">
        <div class="bg-surface-container-high p-1 rounded-full flex items-center">
          <button @click="currentView = 'list'"
            class="px-6 py-1.5 rounded-full font-label-sm transition-all duration-200 text-sm"
            :class="currentView === 'list'
              ? 'bg-secondary-container text-on-secondary-container shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-variant'">
            List View
          </button>
          <button @click="currentView = 'map'"
            class="px-6 py-1.5 rounded-full font-label-sm transition-all duration-200 text-sm"
            :class="currentView === 'map'
              ? 'bg-secondary-container text-on-secondary-container shadow-sm'
              : 'text-on-surface-variant hover:bg-surface-variant'">
            Map View
          </button>
        </div>
        <button @click="showFilters = !showFilters" class="flex items-center gap-2 px-4 py-2 border border-outline-variant rounded-full font-label-sm hover:bg-surface-container-high transition-colors relative">
          <span class="material-symbols-outlined text-sm">tune</span>
          Filters
          <span v-if="activeFilterCount" class="absolute -top-1.5 -right-1.5 w-4 h-4 bg-primary text-on-primary text-[10px] font-bold rounded-full flex items-center justify-center">{{ activeFilterCount }}</span>
        </button>
      </div>

      <div v-if="jobsStore.loading" class="flex items-center justify-center py-20">
        <span class="material-symbols-outlined text-primary text-4xl animate-spin">progress_activity</span>
      </div>

      <!-- Welcome state -->
      <div v-if="!jobsStore.jobs.length && !jobsStore.matches.length && !jobsStore.loading && !jobsStore.location" class="text-center py-16 lg:py-24 px-4">
        <span class="material-symbols-outlined text-6xl text-primary mb-8 block">explore</span>
        <h2 class="font-headline-md text-headline-md lg:text-[28px] text-on-surface mb-4">Find Your Next Role</h2>
        <p class="text-lg text-on-surface-variant max-w-2xl mx-auto mb-10 leading-8">
          <template v-if="resumeStore.profile">Your resume is ready. Search a location above to discover jobs matched to your profile.</template>
          <template v-else>Search for a location above to discover jobs, or upload your resume to get personalized matches.</template>
        </p>
        <div v-if="!resumeStore.profile" class="flex flex-col sm:flex-row gap-md justify-center">
          <router-link to="/upload" class="bg-primary text-on-primary px-6 py-3 rounded-lg font-label-md inline-block">Upload Resume</router-link>
        </div>
      </div>

      <div v-if="showFilters" class="mb-md p-md bg-surface-container-lowest border border-outline-variant rounded-xl shadow-sm">
        <div class="flex flex-wrap gap-md items-end">
          <div>
            <label class="block text-label-sm text-on-surface-variant mb-1">Job Type</label>
            <select v-model="filters.jobType" class="border border-outline-variant rounded-lg px-3 py-2 bg-surface-container-low text-sm">
              <option value="">All</option>
              <option value="full-time">Full-time</option>
              <option value="part-time">Part-time</option>
              <option value="contract">Contract</option>
              <option value="internship">Internship</option>
              <option value="temporary">Temporary</option>
            </select>
          </div>
          <div>
            <label class="block text-label-sm text-on-surface-variant mb-1">Salary Min</label>
            <select v-model="filters.salaryMin" class="border border-outline-variant rounded-lg px-3 py-2 bg-surface-container-low text-sm">
              <option value="">Any</option>
              <option value="50000">$50K</option>
              <option value="100000">$100K</option>
              <option value="150000">$150K</option>
              <option value="200000">$200K</option>
            </select>
          </div>
          <button @click="clearFilters" class="px-4 py-2 border border-outline-variant rounded-lg text-sm hover:bg-surface-container-high">Clear</button>
        </div>
      </div>

      <div v-if="currentView === 'list' && !jobsStore.loading && (jobsStore.jobs.length || jobsStore.matches.length)">
        <div v-if="displayJobs.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
          <JobCard v-for="item in displayJobs" :key="item.job?.id || item.id"
            :job="item.job || item" :match-score="item.score" />
        </div>
        <div v-else class="text-center py-20 text-on-surface-variant">
          <span class="material-symbols-outlined text-5xl mb-4 block">search_off</span>
          <p v-if="activeFilterCount">No jobs match your filters. Try adjusting them.</p>
          <p v-else>No jobs found for this location. Try searching a different area.</p>
        </div>
      </div>

      <div v-if="currentView === 'map' && !jobsStore.loading && (jobsStore.jobs.length || jobsStore.matches.length)" class="relative">
        <div class="h-[500px] lg:h-[600px] w-full rounded-2xl overflow-hidden shadow-lg border border-outline-variant relative transition-all duration-500">
          <div v-if="mapLoading" class="absolute inset-0 bg-surface-container-high animate-pulse flex items-center justify-center z-10">
            <span class="material-symbols-outlined text-primary text-4xl animate-spin">progress_activity</span>
          </div>
          <JobMap :jobs="mapJobs" :center="mapCenter" :zoom="mapZoom" @pin-click="onPinClick" />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useJobsStore } from '../stores/jobs'
import { useMapStore } from '../stores/map'
import { useResumeStore } from '../stores/resume'
import SearchBar from '../components/SearchBar.vue'
import JobCard from '../components/JobCard.vue'
import JobMap from '../components/JobMap.vue'

const router = useRouter()
const jobsStore = useJobsStore()
const mapStore = useMapStore()
const resumeStore = useResumeStore()
const currentView = ref('list')
const mapLoading = ref(false)
const showFilters = ref(false)
const filters = ref({ jobType: '', salaryMin: '' })

const activeFilterCount = computed(() => {
  let count = 0
  if (filters.value.jobType) count++
  if (filters.value.salaryMin) count++
  return count
})

const filteredJobs = computed(() => {
  let source = jobsStore.matches.length ? jobsStore.matches.map(m => m.job) : jobsStore.jobs
  if (filters.value.jobType) {
    const t = filters.value.jobType.toLowerCase()
    source = source.filter(j => (j.job_type || '').toLowerCase().includes(t))
  }
  if (filters.value.salaryMin) {
    const min = parseInt(filters.value.salaryMin)
    source = source.filter(j => {
      if (!j.salary) return false
      const nums = j.salary.match(/\d+/g)
      return nums && nums.some(n => parseInt(n) >= min)
    })
  }
  return source
})

function clearFilters() {
  filters.value = { jobType: '', salaryMin: '' }
}

const displayJobs = computed(() => {
  if (jobsStore.matches.length) return jobsStore.matches
  return filteredJobs.value.map(j => ({ job: j }))
})

const mapJobs = computed(() => {
  return filteredJobs.value.filter(j => j.latitude && j.longitude)
})

const mapCenter = computed(() => {
  if (mapStore.center[0] !== 20 || mapStore.center[1] !== 0) return mapStore.center
  const first = mapJobs.value[0]
  if (first && first.latitude && first.longitude) {
    return [first.latitude, first.longitude]
  }
  return [20, 0]
})

const mapZoom = computed(() => {
  if (mapStore.zoom !== 2) return mapStore.zoom
  const lats = mapJobs.value.map(j => j.latitude).filter(Boolean)
  if (!lats.length) return 2
  const spread = Math.max(...lats) - Math.min(...lats)
  if (spread < 0.5) return 11
  if (spread < 2) return 9
  if (spread < 10) return 6
  return 4
})

watch(currentView, (val) => {
  if (val === 'map') {
    mapLoading.value = true
    setTimeout(() => { mapLoading.value = false }, 1000)
  }
})

function onPinClick(job) {
  router.push(`/jobs/${job.id}`)
}

async function handleSearch(title, location) {
  if (!location) return
  jobsStore.location = location
  await jobsStore.scrapeJobs(location, title)
  if (resumeStore.resumeId) {
    await jobsStore.matchJobs(resumeStore.resumeId, location)
  }
}
</script>


