<template>
  <div class="pb-24">
    <header class="bg-background w-full top-0 sticky z-40">
      <div class="flex items-center justify-between px-md py-sm max-w-5xl mx-auto">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-primary">explore</span>
          <h1 class="font-headline-md text-headline-md font-bold text-primary tracking-tight">GeoHire</h1>
        </div>
        <button class="hover:opacity-80 transition-opacity active:scale-95 p-2">
          <span class="material-symbols-outlined text-on-surface-variant">notifications</span>
        </button>
      </div>
    </header>

    <main class="max-w-5xl mx-auto px-container-margin pt-sm">
      <SearchBar @search="handleSearch" />

      <div v-if="jobsStore.error && !jobsStore.jobs.length" class="mb-md p-md bg-error-container text-on-error-container rounded-xl text-sm">
        {{ jobsStore.error }}
        <button @click="loadMock" class="ml-2 underline font-semibold">Load sample data</button>
      </div>

      <div v-if="jobsStore.jobs.length || jobsStore.matches.length" class="flex items-center justify-between mb-md">
        <ViewToggle :view="currentView" @toggle="currentView = $event" />
        <button class="flex items-center gap-2 px-4 py-2 border border-outline-variant rounded-full font-label-sm hover:bg-surface-container-high transition-colors">
          <span class="material-symbols-outlined text-sm">tune</span>
          Filters
        </button>
      </div>

      <div v-if="jobsStore.loading" class="flex items-center justify-center py-20">
        <span class="material-symbols-outlined text-primary text-4xl animate-spin">progress_activity</span>
      </div>

      <!-- Welcome state -->
      <div v-if="!jobsStore.jobs.length && !jobsStore.matches.length && !jobsStore.loading && !jobsStore.location" class="text-center py-16">
        <span class="material-symbols-outlined text-6xl text-primary mb-6 block">explore</span>
        <h2 class="font-headline-md text-headline-md text-on-surface mb-2">Find Your Next Role</h2>
        <p class="font-body-md text-body-md text-on-surface-variant max-w-md mx-auto mb-8">Search for a location above to discover jobs, or upload your resume to get personalized matches.</p>
        <div class="flex flex-col sm:flex-row gap-md justify-center">
          <router-link to="/upload" class="bg-primary text-on-primary px-lg py-sm rounded-lg font-label-md inline-block">Upload Resume</router-link>
          <button @click="loadMock" class="border border-outline-variant px-lg py-sm rounded-lg font-label-md text-on-surface hover:bg-surface-container-high">Browse sample jobs</button>
        </div>
      </div>

      <div v-if="currentView === 'list' && !jobsStore.loading && (jobsStore.jobs.length || jobsStore.matches.length)">
        <div v-if="displayJobs.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md">
          <JobCard v-for="item in displayJobs" :key="item.job?.id || item.id"
            :job="item.job || item" :match-score="item.score" />
        </div>
        <div v-else class="text-center py-20 text-on-surface-variant">
          <span class="material-symbols-outlined text-5xl mb-4 block">search_off</span>
          <p>No jobs found for this location. Try searching a different area.</p>
        </div>
      </div>

      <div v-if="currentView === 'map' && !jobsStore.loading && (jobsStore.jobs.length || jobsStore.matches.length)" class="relative">
        <JobMap :jobs="mapJobs" :center="mapCenter" :zoom="11" :style="{ height: mapJobs.length ? '600px' : '400px' }" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useJobsStore } from '../stores/jobs'
import { useMapStore } from '../stores/map'
import { useResumeStore } from '../stores/resume'
import SearchBar from '../components/SearchBar.vue'
import ViewToggle from '../components/ViewToggle.vue'
import JobCard from '../components/JobCard.vue'
import JobMap from '../components/JobMap.vue'

const jobsStore = useJobsStore()
const mapStore = useMapStore()
const resumeStore = useResumeStore()
const currentView = ref('list')

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
