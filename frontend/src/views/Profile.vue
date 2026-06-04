<template>
  <div class="pb-32 px-container-margin max-w-2xl mx-auto">
    <header class="w-full top-0 sticky bg-background z-40 flex items-center justify-between px-0 py-sm">
      <h1 class="font-headline-md text-headline-md font-bold text-primary">Profile</h1>
    </header>

    <section class="mt-lg">
      <h2 class="font-headline-sm text-headline-sm mb-md">Your Resume</h2>
      <div v-if="resumeStore.profile" class="bg-white border border-outline-variant p-md rounded-xl shadow-sm">
        <p class="text-body-sm text-on-surface-variant mb-sm">Skills: {{ resumeStore.profile.skills?.join(', ') }}</p>
        <p v-if="resumeStore.profile.experience_years" class="text-body-sm text-on-surface-variant mb-sm">Experience: {{ resumeStore.profile.experience_years }} years</p>
        <button @click="resumeStore.clear()" class="text-error text-label-sm mt-sm hover:underline">Remove Resume</button>
      </div>
      <div v-else class="bg-white border border-outline-variant p-md rounded-xl shadow-sm text-center text-on-surface-variant">
        <p>No resume uploaded yet.</p>
        <router-link to="/upload" class="text-primary font-label-md mt-sm inline-block hover:underline">Upload Resume</router-link>
      </div>
    </section>

    <section class="mt-lg">
      <h2 class="font-headline-sm text-headline-sm mb-md">Bookmarked Jobs</h2>
      <div v-if="bookmarkedJobs.length" class="space-y-md">
        <div v-for="job in bookmarkedJobs" :key="job.id"
          class="bg-white border border-outline-variant p-md rounded-xl shadow-sm cursor-pointer hover:shadow-md transition-shadow"
          @click="$router.push(`/jobs/${job.id}`)">
          <h3 class="font-headline-sm text-headline-sm text-primary">{{ job.title }}</h3>
          <p class="text-body-sm text-on-surface-variant">{{ job.company }} &middot; {{ job.location }}</p>
        </div>
      </div>
      <div v-else class="text-center text-on-surface-variant py-8">
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
