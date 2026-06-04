<template>
  <div class="pb-32 lg:pb-0">
    <header ref="headerRef" class="w-full top-0 sticky z-40 bg-background/80 backdrop-blur-md flex items-center justify-between px-container-margin lg:px-8 py-sm transition-shadow duration-300"
      :class="{ 'shadow-md': scrolled }">
      <button @click="$router.back()"
        class="w-11 h-11 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors active:scale-95 text-on-surface-variant">
        <span class="material-symbols-outlined">arrow_back</span>
      </button>
      <div class="flex gap-2">
        <button class="w-11 h-11 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors active:scale-95 text-on-surface-variant">
          <span class="material-symbols-outlined">share</span>
        </button>
        <button class="w-11 h-11 flex items-center justify-center rounded-full hover:bg-surface-container-high transition-colors active:scale-95 text-on-surface-variant">
          <span class="material-symbols-outlined">bookmark</span>
        </button>
      </div>
    </header>

    <main v-if="job" class="max-w-5xl mx-auto px-container-margin lg:px-8 pt-4 lg:pt-8">
      <section class="mt-lg mb-xl text-center lg:text-left lg:flex lg:items-start lg:gap-8">
        <div class="relative inline-block mb-md lg:mb-0 lg:shrink-0">
          <div class="w-24 h-24 rounded-2xl overflow-hidden bg-white shadow-md border border-outline-variant p-4 flex items-center justify-center">
            <span class="text-primary text-3xl font-bold">{{ job.company.charAt(0) }}</span>
          </div>
        </div>
        <div class="lg:flex-1">
          <h1 class="font-headline-lg-mobile text-headline-lg-mobile md:font-headline-lg md:text-headline-lg text-on-background mb-xs">{{ job.title }}</h1>
          <p class="font-headline-sm text-headline-sm text-primary mb-md">{{ job.company }}</p>
          <div class="flex flex-wrap justify-center lg:justify-start gap-sm">
            <div class="bg-surface-container-high px-md py-1.5 rounded-full flex items-center gap-xs">
              <span class="material-symbols-outlined text-[18px] text-on-surface-variant">location_on</span>
              <span class="font-label-md text-label-md text-on-surface-variant">{{ job.location }}</span>
            </div>
            <div v-if="job.job_type" class="bg-surface-container-high px-md py-1.5 rounded-full flex items-center gap-xs">
              <span class="material-symbols-outlined text-[18px] text-on-surface-variant">schedule</span>
              <span class="font-label-md text-label-md text-on-surface-variant">{{ job.job_type }}</span>
            </div>
            <div v-if="job.salary" class="bg-surface-container-high px-md py-1.5 rounded-full flex items-center gap-xs">
              <span class="material-symbols-outlined text-[18px] text-on-surface-variant">payments</span>
              <span class="font-label-md text-label-md text-on-surface-variant">{{ job.salary }}</span>
            </div>
          </div>
        </div>
      </section>

      <div class="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div class="lg:col-span-3 space-y-6">
          <MatchScore v-if="matchScore !== undefined" :score="matchScore" :skills="matchedSkills" />

          <article class="bg-white border border-outline-variant p-6 lg:p-8 rounded-xl shadow-sm">
            <h2 class="font-headline-sm text-headline-sm mb-4 text-on-background border-l-4 border-primary pl-4">Job Description</h2>
            <p class="text-on-surface-variant leading-relaxed">{{ job.description }}</p>
          </article>

          <article v-if="job.requirements?.length" class="bg-white border border-outline-variant p-6 lg:p-8 rounded-xl shadow-sm">
            <h2 class="font-headline-sm text-headline-sm mb-4 text-on-background border-l-4 border-primary pl-4">Requirements</h2>
            <ul class="space-y-3">
              <li v-for="req in job.requirements" :key="req" class="flex items-start gap-3 text-on-surface-variant">
                <div class="w-1.5 h-1.5 rounded-full bg-primary mt-2.5 shrink-0"></div>
                <span>{{ req }}</span>
              </li>
            </ul>
          </article>
        </div>

        <aside class="space-y-4">
          <div class="bg-surface-container-low border border-outline-variant p-4 rounded-xl">
            <h3 class="font-label-md text-label-md text-on-surface uppercase tracking-wider mb-2">Department</h3>
            <p class="text-on-surface-variant">Experience Design</p>
          </div>
          <div class="bg-surface-container-low border border-outline-variant p-4 rounded-xl">
            <h3 class="font-label-md text-label-md text-on-surface uppercase tracking-wider mb-2">Posted</h3>
            <p class="text-on-surface-variant">2 days ago</p>
          </div>
          <div class="bg-surface-container-low border border-outline-variant p-4 rounded-xl">
            <h3 class="font-label-md text-label-md text-on-surface uppercase tracking-wider mb-2">Candidates</h3>
            <p class="text-on-surface-variant">42 Applicants</p>
          </div>
          <div class="rounded-xl overflow-hidden h-40 border border-outline-variant relative bg-surface-container">
            <div class="absolute inset-0 flex items-center justify-center text-on-surface-variant">
              <div class="text-center">
                <span class="material-symbols-outlined text-2xl block mb-1">map</span>
                <span class="text-label-sm">{{ job.location }}</span>
              </div>
            </div>
            <div class="absolute bottom-2 left-2 right-2 bg-white/90 backdrop-blur px-sm py-1 rounded-lg text-center">
              <span class="font-label-sm text-label-sm text-primary">Office Location</span>
            </div>
          </div>
        </aside>
      </div>
    </main>

    <div v-if="job" class="fixed bottom-0 left-0 w-full z-50 lg:pl-64 px-container-margin lg:px-8 pb-lg lg:pb-6 pt-md bg-white/80 backdrop-blur-xl border-t border-outline-variant/30 flex justify-center items-center">
      <div class="max-w-5xl w-full flex gap-md">
        <button class="w-14 h-14 border border-outline-variant rounded-xl flex items-center justify-center bg-white hover:bg-surface-container-high transition-colors active:scale-90">
          <span class="material-symbols-outlined text-on-surface-variant">favorite</span>
        </button>
        <button @click="handleApply"
          class="flex-1 bg-primary text-on-primary font-headline-sm text-headline-sm py-md rounded-xl shadow-lg shadow-primary/20 transition-all active:scale-[0.98] flex items-center justify-center gap-sm"
          :class="applied ? 'bg-secondary text-on-secondary' : 'hover:bg-primary-container hover:text-on-primary-container'"
          :disabled="applied">
          <template v-if="!applied">
            Apply Now
            <span class="material-symbols-outlined">arrow_forward</span>
          </template>
          <template v-else-if="applying">
            <span class="material-symbols-outlined animate-spin">progress_activity</span>
            Processing...
          </template>
          <template v-else>
            <span class="material-symbols-outlined">check</span>
            Application Sent!
          </template>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useJobsStore } from '../stores/jobs'
import { useResumeStore } from '../stores/resume'
import MatchScore from '../components/MatchScore.vue'

const route = useRoute()
const jobsStore = useJobsStore()
const resumeStore = useResumeStore()
const scrolled = ref(false)
const applied = ref(false)
const applying = ref(false)
const headerRef = ref(null)

const job = computed(() => {
  return jobsStore.jobs.find(j => j.id === route.params.id)
    || jobsStore.matches.find(m => m.job?.id === route.params.id)?.job
    || null
})

const match = computed(() => jobsStore.matches.find(m => m.job?.id === route.params.id))
const matchScore = computed(() => match.value?.score)
const matchedSkills = computed(() => resumeStore.profile?.skills?.slice(0, 4) || [])

function handleApply() {
  applying.value = true
  setTimeout(() => {
    applying.value = false
    applied.value = true
    setTimeout(() => { applied.value = false }, 3000)
  }, 1500)
}

function onScroll() {
  scrolled.value = window.scrollY > 20
}

onMounted(() => window.addEventListener('scroll', onScroll))
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>
