<template>
  <div class="h-screen w-full overflow-hidden flex flex-col">
    <header class="w-full bg-background z-40 shrink-0">
      <div class="flex items-center justify-between px-md py-sm">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-primary">explore</span>
          <span class="font-headline-md text-headline-md font-bold text-primary">GeoHire</span>
        </div>
      </div>
      <div class="px-md pb-sm">
        <div class="relative flex items-center">
          <span class="material-symbols-outlined absolute left-3 text-on-surface-variant">search</span>
          <input v-model="searchQuery" @keyup.enter="searchLocation"
            class="w-full h-11 pl-10 pr-4 bg-surface-container border border-outline-variant rounded-full text-body-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
            placeholder="Search location..." type="text" />
          <span class="material-symbols-outlined absolute right-3 text-primary">my_location</span>
        </div>
      </div>
    </header>

    <main class="flex-1 relative">
      <JobMap :jobs="mapJobs" :center="mapStore.center" :zoom="mapStore.zoom"
        @update:center="mapStore.setCenter" @update:zoom="setZoom" />
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMapStore } from '../stores/map'
import { useJobsStore } from '../stores/jobs'
import JobMap from '../components/JobMap.vue'

const mapStore = useMapStore()
const jobsStore = useJobsStore()
const searchQuery = ref('')

const mapJobs = computed(() => jobsStore.jobs.filter(j => j.latitude && j.longitude))

function searchLocation() {
  if (searchQuery.value) {
    jobsStore.fetchJobs(searchQuery.value)
  }
}

function setZoom(z) {
  mapStore.zoom = z
}
</script>
