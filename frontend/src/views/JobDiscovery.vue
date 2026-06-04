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

      <div v-if="currentView === 'list' && !jobsStore.loading">
        <div v-if="displayJobs.length" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-md">
          <JobCard v-for="item in displayJobs" :key="item.job?.id || item.id"
            :job="item.job || item" :match-score="item.score" />
        </div>
        <div v-else-if="jobsStore.location" class="text-center py-20 text-on-surface-variant">
          <span class="material-symbols-outlined text-5xl mb-4 block">search_off</span>
          <p>No jobs found for this location. Try searching a different area.</p>
        </div>
      </div>

      <div v-if="currentView === 'map' && !jobsStore.loading" class="relative">
        <JobMap :jobs="mapJobs" :center="mapCenter" :zoom="11" />
        <div v-if="mapStore.selectedJob"
          class="absolute bottom-4 left-4 right-4 z-40 bg-surface-container-lowest p-md rounded-xl shadow-xl border border-outline-variant flex items-center gap-md cursor-pointer"
          @click="$router.push(`/jobs/${mapStore.selectedJob.id}`)">
          <div class="w-14 h-14 rounded-lg bg-surface-container flex items-center justify-center text-primary font-bold text-xl shrink-0">
            {{ mapStore.selectedJob.company.charAt(0) }}
          </div>
          <div class="flex-grow min-w-0">
            <h3 class="font-headline-sm text-headline-sm text-on-surface truncate">{{ mapStore.selectedJob.title }}</h3>
            <p class="text-body-sm text-on-surface-variant">{{ mapStore.selectedJob.company }}</p>
            <span v-if="mapStore.selectedJob.salary" class="text-label-md text-primary">{{ mapStore.selectedJob.salary }}</span>
          </div>
        </div>
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

async function handleSearch(title, location) {
  if (!location) return
  await jobsStore.fetchJobs(location)
  if (!jobsStore.jobs.length) {
    await jobsStore.scrapeJobs(location)
  }
  if (resumeStore.resumeId) {
    await jobsStore.matchJobs(resumeStore.resumeId, location)
  }
}
</script>
