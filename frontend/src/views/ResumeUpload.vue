<template>
  <div class="pb-32">
    <header class="w-full top-0 sticky bg-background z-40 flex items-center justify-between px-md py-sm">
      <div class="flex items-center gap-sm">
        <span class="material-symbols-outlined text-primary">explore</span>
        <span class="font-headline-md text-headline-md font-bold text-primary">GeoHire</span>
      </div>
      <button class="p-2 active:scale-95 transition-transform">
        <span class="material-symbols-outlined text-on-surface-variant">notifications</span>
      </button>
    </header>

    <main class="px-container-margin md:max-w-4xl md:mx-auto">
      <section class="mt-xl text-center">
        <h1 class="font-headline-lg-mobile text-headline-lg-mobile md:font-headline-lg md:text-headline-lg text-on-background mb-sm">Ready for Your Next Move?</h1>
        <p class="font-body-md text-body-md text-on-surface-variant max-w-md mx-auto">Upload your resume to see matching jobs and get personalized career insights.</p>
      </section>

      <section class="mt-xl">
        <UploadZone @file-selected="handleFile" />

        <div v-if="resumeStore.uploading" class="mt-md text-center text-on-surface-variant">
          <span class="material-symbols-outlined animate-spin inline-block mr-2">progress_activity</span>
          Parsing your resume...
        </div>

        <div v-if="resumeStore.profile" class="mt-md p-md bg-surface-container-lowest border border-outline-variant rounded-xl">
          <h3 class="font-headline-sm text-headline-sm text-primary mb-sm">Resume Parsed</h3>
          <p class="text-body-sm text-on-surface-variant mb-sm">Skills: {{ resumeStore.profile.skills?.join(', ') }}</p>
          <p v-if="resumeStore.profile.experience_years" class="text-body-sm text-on-surface-variant mb-sm">Experience: {{ resumeStore.profile.experience_years }} years</p>
          <router-link to="/"
            class="inline-block bg-primary text-on-primary px-lg py-sm rounded-lg font-label-md mt-sm active:scale-95 transition-transform">
            Find Matching Jobs
          </router-link>
        </div>
      </section>

      <section class="mt-xl pb-12">
        <h3 class="font-headline-sm text-headline-sm text-on-background mb-md">How AI Matching Works</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-md">
          <div class="bg-white border border-outline-variant p-md rounded-xl shadow-sm">
            <div class="w-10 h-10 rounded-lg bg-secondary-container flex items-center justify-center mb-sm">
              <span class="material-symbols-outlined text-on-secondary-container">psychology</span>
            </div>
            <h4 class="font-headline-sm text-[18px] text-on-surface mb-xs">Skills Analysis</h4>
            <p class="font-body-sm text-body-sm text-on-surface-variant">Our engine parses your experience to identify strengths and technical proficiencies.</p>
          </div>
          <div class="bg-white border border-outline-variant p-md rounded-xl shadow-sm">
            <div class="w-10 h-10 rounded-lg bg-primary-container/10 flex items-center justify-center mb-sm">
              <span class="material-symbols-outlined text-primary">analytics</span>
            </div>
            <h4 class="font-headline-sm text-[18px] text-on-surface mb-xs">Industry Fit</h4>
            <p class="font-body-sm text-body-sm text-on-surface-variant">We map your trajectory against market demands to find roles where you'll have the highest impact.</p>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { useResumeStore } from '../stores/resume'
import UploadZone from '../components/UploadZone.vue'

const resumeStore = useResumeStore()

async function handleFile(file) {
  await resumeStore.uploadResume(file)
}
</script>
