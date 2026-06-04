<template>
  <div class="pb-32 lg:pb-0 px-container-margin lg:px-8 max-w-5xl mx-auto pt-4 lg:pt-8">
    <header class="w-full top-0 sticky bg-background z-40 flex items-center justify-between px-0 py-sm">
      <h1 class="font-headline-md text-headline-md font-bold text-primary">Profile</h1>
    </header>

    <section class="mt-lg lg:mt-8">
      <h2 class="font-headline-sm text-headline-sm mb-4">Your Resume</h2>
      <div v-if="resumeStore.profile" class="bg-white border border-outline-variant p-5 lg:p-6 rounded-xl shadow-sm">
        <div class="mb-4">
          <label class="text-label-sm text-outline block mb-1">Skills</label>
          <input v-model="form.skills" type="text"
            class="w-full border border-outline-variant rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none" />
        </div>
        <div class="mb-4">
          <label class="text-label-sm text-outline block mb-1">Experience (years)</label>
          <input v-model.number="form.experience_years" type="number" min="0" step="0.5"
            class="w-full border border-outline-variant rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none" />
        </div>
        <div class="mb-4">
          <label class="text-label-sm text-outline block mb-1">Job Title Keywords</label>
          <input v-model="form.job_title_keywords" type="text"
            class="w-full border border-outline-variant rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none" />
        </div>
        <div class="mb-4">
          <label class="text-label-sm text-outline block mb-1">Summary</label>
          <textarea v-model="form.summary" rows="3"
            class="w-full border border-outline-variant rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary focus:border-transparent outline-none resize-none"></textarea>
        </div>
        <div class="flex items-center gap-3">
          <button @click="saveProfile" class="bg-primary text-on-primary px-5 py-2 rounded-lg font-label-md text-sm hover:opacity-90 transition-opacity">Save</button>
          <button @click="resetForm" class="text-on-surface-variant text-sm hover:underline">Reset</button>
          <button @click="resumeStore.clear()" class="text-error text-sm ml-auto hover:underline">Remove Resume</button>
        </div>
      </div>
      <div v-else class="bg-white border border-outline-variant p-8 lg:p-10 rounded-xl shadow-sm text-center text-on-surface-variant">
        <span class="material-symbols-outlined text-5xl text-outline mb-4 block">description</span>
        <p class="mb-4">No resume uploaded yet.</p>
        <router-link to="/upload" class="bg-primary text-on-primary px-6 py-3 rounded-lg font-label-md inline-block hover:opacity-90 transition-opacity">Upload Resume</router-link>
      </div>
    </section>

    <section class="mt-lg lg:mt-10">
      <h2 class="font-headline-sm text-headline-sm mb-4">My Home</h2>
      <div class="bg-white border border-outline-variant rounded-xl shadow-sm overflow-hidden">
        <div class="relative" style="height: 250px;">
          <l-map ref="homeMapRef" :zoom="homeZoom" :center="homeCenter" :useGlobalLeaflet="false" :options="{ zoomControl: false }"
            @ready="onHomeMapReady"
            style="height: 100%; width: 100%;">
            <l-tile-layer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution="&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a>" />
            <l-marker v-if="homeLat != null" :lat-lng="[homeLat, homeLng]" :icon="homeIcon" />
          </l-map>
        </div>
        <div class="p-4 lg:p-5">
          <p v-if="homeLat != null" class="text-sm text-on-surface-variant mb-3">
            Home: {{ homeLat.toFixed(4) }}, {{ homeLng.toFixed(4) }}
          </p>
          <p v-else class="text-sm text-on-surface-variant mb-3">
            Click on the map above to drop a pin at your home location.
          </p>
          <div class="flex items-center gap-3">
            <button @click="saveHome"
              :disabled="homeLat == null || (homeLat === resumeStore.homeLatitude && homeLng === resumeStore.homeLongitude)"
              class="bg-primary text-on-primary px-5 py-2 rounded-lg font-label-md text-sm hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed">
              {{ resumeStore.homeLatitude != null ? 'Update' : 'Save' }} Home
            </button>
            <button v-if="resumeStore.homeLatitude != null" @click="removeHome" class="text-error text-sm hover:underline">Remove</button>
          </div>
        </div>
      </div>
    </section>

    <section class="mt-lg lg:mt-10 mb-8">
      <h2 class="font-headline-sm text-headline-sm mb-4">Bookmarked Jobs</h2>
      <div v-if="bookmarkedJobs.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div v-for="job in bookmarkedJobs" :key="job.id"
          class="bg-white border border-outline-variant p-4 lg:p-5 rounded-xl shadow-sm cursor-pointer hover:shadow-md transition-shadow"
          @click="$router.push(`/jobs/${job.id}`)">
          <h3 class="font-headline-sm text-headline-sm text-primary">{{ job.title }}</h3>
          <p class="text-body-sm text-on-surface-variant">{{ job.company }} &middot; {{ job.location }}</p>
        </div>
      </div>
      <div v-else class="text-center text-on-surface-variant py-12 bg-white border border-outline-variant rounded-xl">
        <span class="material-symbols-outlined text-4xl text-outline mb-3 block">bookmark_border</span>
        <p>No bookmarked jobs.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { useResumeStore } from '../stores/resume'
import { useJobsStore } from '../stores/jobs'
import { LMap, LTileLayer, LMarker } from '@vue-leaflet/vue-leaflet'
import L from 'leaflet'

const resumeStore = useResumeStore()
const jobsStore = useJobsStore()

const form = reactive({
  skills: '',
  experience_years: null,
  job_title_keywords: '',
  summary: '',
})

const homeMapRef = ref(null)
const homeLat = ref(resumeStore.homeLatitude)
const homeLng = ref(resumeStore.homeLongitude)
const homeZoom = ref(resumeStore.homeLatitude != null ? 11 : 4)
const homeCenter = ref(
  resumeStore.homeLatitude != null
    ? [resumeStore.homeLatitude, resumeStore.homeLongitude]
    : [20, 78]
)

const homeIcon = L.divIcon({
  html: '<span class="material-symbols-outlined text-3xl" style="color:#dc2626;filter:drop-shadow(0 0 4px rgba(0,0,0,0.5))">home_pin</span>',
  className: '',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
})

watch(() => resumeStore.profile, (p) => {
  if (p) resetForm()
}, { immediate: true })

function resetForm() {
  const p = resumeStore.profile
  if (!p) return
  form.skills = (p.skills || []).join(', ')
  form.experience_years = p.experience_years ?? null
  form.job_title_keywords = (p.job_title_keywords || []).join(', ')
  form.summary = p.summary || ''
}

function saveProfile() {
  resumeStore.updateProfile({
    skills: form.skills.split(',').map(s => s.trim()).filter(Boolean),
    experience_years: form.experience_years,
    job_title_keywords: form.job_title_keywords.split(',').map(s => s.trim()).filter(Boolean),
    summary: form.summary,
  })
}

function onHomeMapReady(map) {
  map.on('click', (e) => {
    homeLat.value = e.latlng.lat
    homeLng.value = e.latlng.lng
  })
}

function saveHome() {
  if (homeLat.value != null) {
    resumeStore.setHomeLocation(homeLat.value, homeLng.value)
  }
}

function removeHome() {
  homeLat.value = null
  homeLng.value = null
  resumeStore.setHomeLocation(null, null)
}

const bookmarkedJobs = computed(() => {
  const bookmarks = JSON.parse(localStorage.getItem('geohire_bookmarks') || '[]')
  return jobsStore.jobs.filter(j => bookmarks.includes(j.id))
})
</script>
