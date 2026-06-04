<template>
  <div class="pb-32 lg:pb-0">
    <header class="w-full top-0 sticky bg-background z-40 flex items-center justify-between px-container-margin lg:px-8 py-sm transition-opacity hover:opacity-80">
      <div class="flex items-center gap-sm">
        <span class="material-symbols-outlined text-primary">explore</span>
        <span class="font-headline-md text-headline-md font-bold text-primary">GeoHire</span>
      </div>
      <button class="p-2 active:scale-95 transition-transform">
        <span class="material-symbols-outlined text-on-surface-variant">notifications</span>
      </button>
    </header>

    <main class="max-w-5xl mx-auto px-container-margin lg:px-8 pt-4 lg:pt-8">
      <section class="mt-xl lg:mt-12 text-center lg:text-left">
        <h1 class="font-headline-lg-mobile text-headline-lg-mobile md:font-headline-lg md:text-headline-lg text-on-background mb-sm">Ready for Your Next Move?</h1>
        <p class="font-body-md text-body-md text-on-surface-variant max-w-2xl mx-auto lg:mx-0">Upload your resume to see matching jobs and get personalized career insights.</p>
      </section>

      <section class="mt-xl lg:mt-12 lg:flex lg:gap-8 lg:items-start">
        <div class="lg:flex-1 lg:max-w-2xl">
          <div class="relative overflow-hidden group border-2 border-dashed border-outline-variant bg-surface-container-lowest rounded-xl p-xl lg:p-12 flex flex-col items-center justify-center transition-all duration-300 hover:border-primary cursor-pointer active:scale-[0.98]"
            @click="$refs.input.click()" @dragover.prevent @drop.prevent="handleDrop"
            :class="{ 'border-primary bg-surface-container': isDragging }">
            <div class="absolute inset-0 bg-primary opacity-0 group-hover:opacity-[0.02] transition-opacity"></div>
            <div class="w-20 h-20 rounded-full bg-surface-container flex items-center justify-center mb-md relative">
              <div class="absolute inset-0 rounded-full bg-primary opacity-10 upload-pulse"></div>
              <span class="material-symbols-outlined text-primary text-[40px]">upload_file</span>
            </div>
            <h2 class="font-headline-sm text-headline-sm text-on-surface mb-xs">Drop your resume here</h2>
            <p class="font-body-sm text-body-sm text-on-surface-variant mb-lg">PDF, DOCX up to 10MB</p>
            <button type="button" class="bg-primary text-on-primary px-lg py-sm rounded-lg font-label-md text-label-md shadow-lg active:scale-95 transition-transform">
              Browse Files
            </button>
            <input ref="input" type="file" accept=".pdf,.docx" class="hidden" @change="handleFile" />
          </div>

          <div class="mt-md flex items-center justify-center gap-md">
            <div class="h-px bg-outline-variant flex-1"></div>
            <span class="font-label-sm text-label-sm text-outline uppercase tracking-widest">or</span>
            <div class="h-px bg-outline-variant flex-1"></div>
          </div>
          <button class="w-full mt-md border border-outline-variant py-md rounded-lg flex items-center justify-center gap-sm font-label-md text-label-md text-on-surface hover:bg-surface-container-low transition-colors active:scale-95 transition-transform">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
              <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
            Link LinkedIn Profile
          </button>

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
        </div>

        <!-- Sidebar on desktop -->
        <aside class="hidden lg:block lg:w-80 shrink-0">
          <div class="bg-white border border-outline-variant p-6 rounded-xl shadow-sm">
            <h3 class="font-headline-sm text-headline-sm text-on-background mb-4">Why Upload?</h3>
            <ul class="space-y-4">
              <li class="flex items-start gap-3">
                <span class="material-symbols-outlined text-secondary text-sm shrink-0">check_circle</span>
                <span class="text-body-sm text-on-surface-variant">Get personalized job matches based on your skills</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="material-symbols-outlined text-secondary text-sm shrink-0">check_circle</span>
                <span class="text-body-sm text-on-surface-variant">AI analyzes your experience for hidden strengths</span>
              </li>
              <li class="flex items-start gap-3">
                <span class="material-symbols-outlined text-secondary text-sm shrink-0">check_circle</span>
                <span class="text-body-sm text-on-surface-variant">See your compatibility score for every role</span>
              </li>
            </ul>
          </div>
        </aside>
      </section>

      <section class="mt-xl lg:mt-16 pb-12 lg:pb-16">
        <h3 class="font-headline-sm text-headline-sm text-on-background mb-6">How AI Matching Works</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 lg:gap-6">
          <div class="bg-white border border-outline-variant p-5 lg:p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div class="w-10 h-10 rounded-lg bg-secondary-container flex items-center justify-center mb-sm">
              <span class="material-symbols-outlined text-on-secondary-container">psychology</span>
            </div>
            <h4 class="font-headline-sm text-[18px] text-on-surface mb-xs">Skills Analysis</h4>
            <p class="font-body-sm text-body-sm text-on-surface-variant">Our AI parses your experience to identify hidden strengths and technical proficiencies you might have missed.</p>
          </div>
          <div class="bg-white border border-outline-variant p-5 lg:p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div class="w-10 h-10 rounded-lg bg-primary-container/10 flex items-center justify-center mb-sm">
              <span class="material-symbols-outlined text-primary">analytics</span>
            </div>
            <h4 class="font-headline-sm text-[18px] text-on-surface mb-xs">Industry Fit</h4>
            <p class="font-body-sm text-body-sm text-on-surface-variant">We map your trajectory against current market demands to find roles where you'll have the highest impact.</p>
          </div>
          <div class="bg-white border border-outline-variant p-5 lg:p-6 rounded-xl shadow-sm hover:shadow-md transition-shadow">
            <div class="w-10 h-10 rounded-lg bg-secondary-container flex items-center justify-center mb-sm">
              <span class="material-symbols-outlined text-on-secondary-container">trending_up</span>
            </div>
            <h4 class="font-headline-sm text-[18px] text-on-surface mb-xs">Salary Insights</h4>
            <p class="font-body-sm text-body-sm text-on-surface-variant">Compare compensation across similar roles and locations to negotiate your best offer.</p>
          </div>
          <div class="md:col-span-2 lg:col-span-3 relative h-56 lg:h-64 rounded-xl overflow-hidden group">
            <img src="https://lh3.googleusercontent.com/aida-public/AB6AXuCkVqDTTsB8cqjBYgTI9MTTNCjjv1ArFKIJOKCre8L0qVQ7mrtGlzWOhtACBqlIFRhDo3LSU-CQ3id4XEo46NQiks4xrKCxoq8tKkFBqHPs0peM0r3ZcMolajeJRv3sa-DI4IunHcIYtgpXAPFj2smUhtzEtDWvyPPnXVtjYTdG7UPJH70vdakMHjRN3dGDEAZgFJhWt-bm9l_HyeMwxMwENfi7Bac1hI8BDqQ_qa3mg0sDSvSy46ahZSjTCyl3CsbqRym9Uhe3lnw"
              alt="Career Progress" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105" />
            <div class="absolute inset-0 bg-gradient-to-t from-primary/80 to-transparent flex flex-col justify-end p-6">
              <p class="text-on-primary font-headline-sm text-headline-sm">94% Success Rate</p>
              <p class="text-on-primary/80 font-body-sm text-body-sm">Users who use AI matching find their next role 3x faster.</p>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useResumeStore } from '../stores/resume'

const resumeStore = useResumeStore()
const isDragging = ref(false)
const input = ref(null)

async function handleFile(file) {
  if (file) await resumeStore.uploadResume(file)
}

function handleDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) resumeStore.uploadResume(file)
}
</script>
