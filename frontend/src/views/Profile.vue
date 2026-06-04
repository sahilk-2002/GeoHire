<template>
  <div class="pb-32 lg:pb-0 px-container-margin lg:px-8 max-w-5xl mx-auto pt-4 lg:pt-8">
    <header class="w-full top-0 sticky bg-background z-40 flex items-center justify-between px-0 py-sm">
      <h1 class="font-headline-md text-headline-md font-bold text-primary">Profile</h1>
    </header>

    <section class="mt-lg lg:mt-8">
      <h2 class="font-headline-sm text-headline-sm mb-4">Your Resume</h2>
      <div v-if="resumeStore.profile" class="bg-white border border-outline-variant p-5 lg:p-6 rounded-xl shadow-sm">
        <p class="text-body-sm text-on-surface-variant mb-sm">Skills: {{ resumeStore.profile.skills?.join(', ') }}</p>
        <p v-if="resumeStore.profile.experience_years" class="text-body-sm text-on-surface-variant mb-sm">Experience: {{ resumeStore.profile.experience_years }} years</p>
        <button @click="resumeStore.clear()" class="text-error text-label-sm mt-3 hover:underline">Remove Resume</button>
      </div>
      <div v-else class="bg-white border border-outline-variant p-8 lg:p-10 rounded-xl shadow-sm text-center text-on-surface-variant">
        <span class="material-symbols-outlined text-5xl text-outline mb-4 block">description</span>
        <p class="mb-4">No resume uploaded yet.</p>
        <router-link to="/upload" class="bg-primary text-on-primary px-6 py-3 rounded-lg font-label-md inline-block hover:opacity-90 transition-opacity">Upload Resume</router-link>
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
import { computed } from 'vue'
import { useResumeStore } from '../stores/resume'
import { useJobsStore } from '../stores/jobs'

const resumeStore = useResumeStore()
const jobsStore = useJobsStore()

const bookmarkedJobs = computed(() => {
  const bookmarks = JSON.parse(localStorage.getItem('geohire_bookmarks') || '[]')
  return jobsStore.jobs.filter(j => bookmarks.includes(j.id))
})
</script>
