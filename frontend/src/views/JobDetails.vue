<template>
  <div class="pb-32">
    <header class="w-full top-0 sticky z-40 bg-background/80 backdrop-blur-md flex items-center justify-between px-md py-sm">
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

    <main v-if="job" class="max-w-screen-md mx-auto px-container-margin">
      <section class="mt-lg mb-xl text-center">
        <div class="w-24 h-24 rounded-2xl overflow-hidden bg-white shadow-md border border-outline-variant p-4 flex items-center justify-center mx-auto mb-md">
          <span class="text-primary text-3xl font-bold">{{ job.company.charAt(0) }}</span>
        </div>
        <h1 class="font-headline-lg-mobile text-headline-lg-mobile md:font-headline-lg md:text-headline-lg text-on-background mb-xs">{{ job.title }}</h1>
        <p class="font-headline-sm text-headline-sm text-primary mb-md">{{ job.company }}</p>
        <div class="flex flex-wrap justify-center gap-sm">
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
      </section>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-md">
        <MatchScore v-if="matchScore !== undefined" :score="matchScore" :skills="matchedSkills" class="md:col-span-3" />

        <div class="md:col-span-2 space-y-md">
          <article class="bg-white border border-outline-variant p-lg rounded-xl shadow-sm">
            <h2 class="font-headline-sm text-headline-sm mb-md text-on-background border-l-4 border-primary pl-md">Job Description</h2>
            <p class="text-on-surface-variant leading-relaxed">{{ job.description }}</p>
          </article>

          <article v-if="job.requirements?.length" class="bg-white border border-outline-variant p-lg rounded-xl shadow-sm">
            <h2 class="font-headline-sm text-headline-sm mb-md text-on-background border-l-4 border-primary pl-md">Requirements</h2>
            <ul class="space-y-sm">
              <li v-for="req in job.requirements" :key="req" class="flex items-start gap-md text-on-surface-variant">
                <div class="w-1.5 h-1.5 rounded-full bg-primary mt-2.5 shrink-0"></div>
                <span>{{ req }}</span>
              </li>
            </ul>
          </article>
        </div>

        <aside class="space-y-md">
          <div class="bg-surface-container-low border border-outline-variant p-md rounded-xl">
            <h3 class="font-label-md text-label-md text-on-surface uppercase tracking-wider mb-sm">Source</h3>
            <p class="text-on-surface-variant">{{ job.source }}</p>
          </div>
          <div class="bg-surface-container-low border border-outline-variant p-md rounded-xl">
            <h3 class="font-label-md text-label-md text-on-surface uppercase tracking-wider mb-sm">Company</h3>
            <p class="text-on-surface-variant">{{ job.company }}</p>
          </div>
        </aside>
      </div>
    </main>

    <div v-if="job" class="fixed bottom-0 left-0 w-full z-50 px-container-margin pb-lg pt-md bg-white/80 backdrop-blur-xl border-t border-outline-variant/30 flex justify-center items-center">
      <div class="max-w-screen-md w-full flex gap-md">
        <button class="w-14 h-14 border border-outline-variant rounded-xl flex items-center justify-center bg-white hover:bg-surface-container-high transition-colors active:scale-90">
          <span class="material-symbols-outlined text-on-surface-variant">favorite</span>
        </button>
        <a :href="job.source_url" target="_blank"
          class="flex-1 bg-primary text-on-primary font-headline-sm text-headline-sm py-md rounded-xl shadow-lg shadow-primary/20 hover:bg-primary-container hover:text-on-primary-container transition-all active:scale-[0.98] flex items-center justify-center gap-sm">
          Apply Now
          <span class="material-symbols-outlined">arrow_forward</span>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useJobsStore } from '../stores/jobs'
import { useResumeStore } from '../stores/resume'
import MatchScore from '../components/MatchScore.vue'

const route = useRoute()
const jobsStore = useJobsStore()
const resumeStore = useResumeStore()

const job = computed(() => {
  return jobsStore.jobs.find(j => j.id === route.params.id)
    || jobsStore.matches.find(m => m.job?.id === route.params.id)?.job
    || null
})

const match = computed(() => jobsStore.matches.find(m => m.job?.id === route.params.id))
const matchScore = computed(() => match.value?.score)
const matchedSkills = computed(() => resumeStore.profile?.skills?.slice(0, 4) || [])
</script>
