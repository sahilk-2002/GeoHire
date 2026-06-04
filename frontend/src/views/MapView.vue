<template>
  <div class="h-screen w-full overflow-hidden relative">
    <!-- Map fills the full screen -->
    <div class="absolute inset-0">
      <JobMap :jobs="filteredJobs" :center="mapStore.center" :zoom="mapStore.zoom"
        :draw-active="drawActive" :cleared="clearedCount"
        @update:center="onCenterChange" @update:zoom="onZoomChange" @pin-click="onPinClick"
        @area-drawn="onAreaDrawn" />
      <div class="absolute inset-0 map-gradient-overlay pointer-events-none"></div>
    </div>

    <!-- Header with search -->
    <div class="absolute top-0 left-0 right-0 z-30 bg-gradient-to-b from-background/95 to-background/0 pb-6">
      <div class="px-container-margin lg:px-6 pt-3 lg:pt-4">
        <div class="relative flex items-center max-w-2xl">
          <span class="material-symbols-outlined absolute left-3 text-on-surface-variant">search</span>
          <input v-model="searchQuery" @keyup.enter="searchLocation"
            class="w-full h-11 pl-10 pr-10 bg-surface-container border border-outline-variant rounded-full text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
            placeholder="Search location..." type="text" />
          <button v-if="searchQuery" @click="searchQuery = ''; clearResults()"
            class="absolute right-1 text-on-surface-variant p-2 hover:bg-surface-container-high rounded-full transition-colors">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Loading state -->
    <div v-if="jobsStore.loading" class="absolute inset-0 flex items-center justify-center z-20 bg-background/60">
      <div class="bg-surface-container-lowest px-6 py-4 rounded-xl shadow-lg flex items-center gap-3">
        <span class="material-symbols-outlined text-primary text-2xl animate-spin">progress_activity</span>
        <span class="text-base text-on-surface">Searching jobs in &ldquo;{{ searchQuery }}&rdquo;&hellip;</span>
      </div>
    </div>

    <!-- Empty / search prompt state -->
    <div v-if="!jobsStore.loading && !searched" class="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
      <div class="bg-surface-container-lowest/90 px-6 py-4 rounded-xl shadow-sm text-on-surface-variant text-sm">
        <div class="text-center">
          <span class="material-symbols-outlined text-3xl text-outline block mb-2">map</span>
          Enter a location above to see job pins on the map
        </div>
      </div>
    </div>

    <!-- No results state -->
    <div v-if="!jobsStore.loading && searched && !mapJobs.length && !jobsStore.error" class="absolute inset-0 flex items-center justify-center z-10">
      <div class="bg-surface-container-lowest/90 px-6 py-5 rounded-xl shadow-sm text-center">
        <span class="material-symbols-outlined text-3xl text-outline block mb-2">search_off</span>
        <p class="text-on-surface-variant text-sm mb-3">No jobs found for this location.</p>
        <button @click="loadMock" class="text-primary font-label-md hover:underline">Browse sample jobs instead</button>
      </div>
    </div>

    <!-- Error state -->
    <div v-if="!jobsStore.loading && jobsStore.error && !mapJobs.length" class="absolute inset-0 flex items-center justify-center z-10">
      <div class="bg-surface-container-lowest/90 px-6 py-5 rounded-xl shadow-sm text-center max-w-sm">
        <span class="material-symbols-outlined text-3xl text-error block mb-2">cloud_off</span>
        <p class="text-on-surface-variant text-sm mb-1">{{ jobsStore.error }}</p>
        <button @click="loadMock" class="mt-3 bg-primary text-on-primary px-5 py-2 rounded-lg font-label-md active:scale-95 transition-transform">Load sample data</button>
      </div>
    </div>

    <div class="absolute right-4 lg:right-6" :class="drawActive ? 'top-28 lg:top-28' : 'top-20 lg:top-6'">
      <div v-if="drawActive" class="mb-2 px-3 py-1.5 bg-primary text-on-primary text-xs rounded-full shadow-lg text-center whitespace-nowrap">
        Click & drag to select area
      </div>
      <div class="flex flex-col gap-2">
        <button @click="drawActive = !drawActive"
          class="w-11 h-11 rounded-full shadow-lg flex items-center justify-center active:scale-90 transition-transform"
          :class="drawActive ? 'bg-primary text-on-primary' : 'bg-white text-primary border border-outline-variant/30 hover:bg-surface-container-low'">
          <span class="material-symbols-outlined text-lg">crop_square</span>
        </button>
        <button v-if="areaBounds" @click="clearArea"
          class="w-11 h-11 rounded-full bg-white shadow-lg flex items-center justify-center text-error active:scale-90 transition-transform hover:bg-surface-container-low border border-outline-variant/30">
          <span class="material-symbols-outlined text-lg">close</span>
        </button>
        <button @click="recenter"
          class="w-11 h-11 rounded-full bg-primary text-on-primary shadow-lg flex items-center justify-center active:scale-90 transition-transform hover:opacity-90">
          <span class="material-symbols-outlined text-lg">my_location</span>
        </button>
      </div>
    </div>

    <!-- Mobile slide-up card -->
    <div class="absolute bottom-4 left-4 right-4 z-40 lg:hidden transition-transform duration-300 ease-out"
      :class="selectedJob ? 'translate-y-0' : 'translate-y-[150%]'">
      <div class="bg-surface-container-lowest p-md rounded-xl shadow-xl border border-outline-variant flex items-center gap-md">
        <div class="w-14 h-14 rounded-lg bg-surface-container flex items-center justify-center overflow-hidden flex-shrink-0">
          <span class="text-primary font-bold text-lg">{{ selectedJob?.company?.charAt(0) }}</span>
        </div>
        <div class="flex-grow min-w-0">
          <div class="flex justify-between items-start">
            <h3 class="font-headline-sm text-headline-sm text-on-surface truncate">{{ selectedJob?.title }}</h3>
            <button @click="selectedJob = null" class="text-outline hover:text-on-surface shrink-0 ml-2">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <p class="text-body-sm text-on-surface-variant">{{ selectedJob?.company }} &bull; {{ selectedJob?.location }}</p>
          <div class="mt-2 flex items-center justify-between">
            <span class="text-label-md text-primary">{{ selectedJob?.salary }}</span>
            <router-link :to="`/jobs/${selectedJob?.id}`"
              class="bg-primary text-on-primary text-label-md px-4 py-1.5 rounded-lg active:scale-95 transition-transform inline-block">
              View Details
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Desktop side panel -->
    <div v-if="selectedJob" class="hidden lg:block absolute top-20 left-4 w-80 z-30 max-h-[calc(100%-6rem)] overflow-y-auto">
      <div class="bg-surface-container-lowest rounded-xl shadow-xl border border-outline-variant p-5">
        <div class="flex justify-between items-start mb-4">
          <div class="w-14 h-14 rounded-lg bg-surface-container flex items-center justify-center">
            <span class="text-primary font-bold text-lg">{{ selectedJob.company.charAt(0) }}</span>
          </div>
          <button @click="selectedJob = null" class="text-outline hover:text-on-surface">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <h3 class="font-headline-sm text-headline-sm text-on-surface mb-1">{{ selectedJob.title }}</h3>
        <p class="text-body-sm text-on-surface-variant mb-3">{{ selectedJob.company }} &bull; {{ selectedJob.location }}</p>
        <p v-if="selectedJob.salary" class="text-label-md text-primary mb-4">{{ selectedJob.salary }}</p>
        <p v-if="selectedJob.description" class="text-body-sm text-on-surface-variant mb-4 line-clamp-3">{{ selectedJob.description }}</p>
        <router-link :to="`/jobs/${selectedJob.id}`"
          class="block w-full text-center bg-primary text-on-primary px-4 py-2.5 rounded-lg font-label-md active:scale-95 transition-transform">
          View Full Details
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useMapStore } from '../stores/map'
import { useJobsStore } from '../stores/jobs'
import JobMap from '../components/JobMap.vue'

const router = useRouter()
const mapStore = useMapStore()
const jobsStore = useJobsStore()
const searchQuery = ref('')
const selectedJob = ref(null)
const searched = ref(false)
const drawActive = ref(false)
const areaBounds = ref(null)
const clearedCount = ref(0)

const mapJobs = computed(() => jobsStore.jobs.filter(j => j.latitude && j.longitude))

const filteredJobs = computed(() => {
  if (!areaBounds.value) return mapJobs.value
  const b = areaBounds.value
  return mapJobs.value.filter(j =>
    j.latitude >= b.south && j.latitude <= b.north &&
    j.longitude >= b.west && j.longitude <= b.east
  )
})

async function searchLocation() {
  if (!searchQuery.value) return
  searched.value = true
  selectedJob.value = null
  await jobsStore.fetchJobs(searchQuery.value)
  if (!jobsStore.jobs.length) {
    await jobsStore.scrapeJobs(searchQuery.value)
  }
  if (mapJobs.value.length) {
    recenter()
  }
}

function onAreaDrawn(bounds) {
  areaBounds.value = bounds
  drawActive.value = false
}

function clearArea() {
  areaBounds.value = null
  clearedCount.value++
}

function clearResults() {
  searched.value = false
  jobsStore.jobs = []
  jobsStore.error = ''
  clearArea()
}

function loadMock() {
  jobsStore.loadMockData()
  searched.value = true
  searchQuery.value = 'San Francisco'
  recenter()
}

function onCenterChange(center) {
  mapStore.setCenter(center)
}

function onZoomChange(zoom) {
  mapStore.zoom = zoom
}

function onPinClick(job) {
  selectedJob.value = job
}

function recenter() {
  if (mapJobs.value.length) {
    const avgLat = mapJobs.value.reduce((s, j) => s + j.latitude, 0) / mapJobs.value.length
    const avgLng = mapJobs.value.reduce((s, j) => s + j.longitude, 0) / mapJobs.value.length
    mapStore.setCenter(avgLat, avgLng)
  }
}
</script>
