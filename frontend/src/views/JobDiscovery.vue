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
        <button @click="loadMock" class="ml-2 underline font-semibold">Load sample data</button>
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
        <button class="flex items-center gap-2 px-4 py-2 border border-outline-variant rounded-full font-label-sm hover:bg-surface-container-high transition-colors">
          <span class="material-symbols-outlined text-sm">tune</span>
          Filters
        </button>
      </div>

      <div v-if="jobsStore.loading" class="flex items-center justify-center py-20">
        <span class="material-symbols-outlined text-primary text-4xl animate-spin">progress_activity</span>
      </div>

      <!-- Welcome state -->
      <div v-if="!jobsStore.jobs.length && !jobsStore.matches.length && !jobsStore.loading && !jobsStore.location" class="text-center py-16 lg:py-24 px-4">
        <span class="material-symbols-outlined text-6xl text-primary mb-8 block">explore</span>
        <h2 class="font-headline-md text-headline-md lg:text-[28px] text-on-surface mb-4">Find Your Next Role</h2>
        <p class="text-lg text-on-surface-variant max-w-2xl mx-auto mb-10 leading-8">Search for a location above to discover jobs, or upload your resume to get personalized matches.</p>
        <div class="flex flex-col sm:flex-row gap-md justify-center">
          <router-link to="/upload" class="bg-primary text-on-primary px-6 py-3 rounded-lg font-label-md inline-block">Upload Resume</router-link>
          <button @click="loadMock" class="border border-outline-variant px-6 py-3 rounded-lg font-label-md text-on-surface hover:bg-surface-container-high">Browse sample jobs</button>
        </div>
      </div>

      <div v-if="currentView === 'list' && !jobsStore.loading && (jobsStore.jobs.length || jobsStore.matches.length)">
        <div v-if="displayJobs.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 lg:gap-6">
          <JobCard v-for="item in displayJobs" :key="item.job?.id || item.id"
            :job="item.job || item" :match-score="item.score" />
        </div>
        <div v-else class="text-center py-20 text-on-surface-variant">
          <span class="material-symbols-outlined text-5xl mb-4 block">search_off</span>
          <p>No jobs found for this location. Try searching a different area.</p>
        </div>
      </div>

      <div v-if="currentView === 'map' && !jobsStore.loading && (jobsStore.jobs.length || jobsStore.matches.length)" class="relative">
        <div class="h-[500px] lg:h-[600px] w-full rounded-2xl overflow-hidden shadow-lg border border-outline-variant relative transition-all duration-500">
          <div v-if="mapLoading" class="absolute inset-0 bg-surface-container-high animate-pulse flex items-center justify-center z-10">
            <span class="material-symbols-outlined text-primary text-4xl animate-spin">progress_activity</span>
          </div>
          <JobMap :jobs="mapJobs" :center="mapCenter" :zoom="11" @pin-click="onPinClick" />
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

const displayJobs = computed(() => {
  if (jobsStore.matches.length) return jobsStore.matches
  return jobsStore.jobs.map(j => ({ job: j }))
})

const mapJobs = computed(() => {
  const source = jobsStore.matches.length ? jobsStore.matches.map(m => m.job) : jobsStore.jobs
  return source.filter(j => j.latitude && j.longitude)
})

const mapCenter = computed(() => {
  if (mapStore.center[0] !== 20 || mapStore.center[1] !== 0) return mapStore.center
  return [37.7749, -122.4194]
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

function loadMock() {
  jobsStore.loadMockData()
}

async function handleSearch(title, location) {
  if (!location) return
  jobsStore.location = location
  await jobsStore.fetchJobs(location)
  if (!jobsStore.jobs.length) {
    await jobsStore.scrapeJobs(location)
  }
  if (resumeStore.resumeId) {
    await jobsStore.matchJobs(resumeStore.resumeId, location)
  }
}
</script>


