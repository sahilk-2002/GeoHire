<template>
  <div @click="$router.push(`/jobs/${job.id}`)"
    class="bg-surface-container-lowest border border-outline-variant rounded-xl p-md shadow-sm hover:shadow-md hover:border-primary/30 transition-all cursor-pointer group">
    <div class="flex justify-between items-start mb-4">
      <div class="w-12 h-12 rounded-lg bg-surface-container p-2 flex items-center justify-center text-primary font-bold text-lg">
        {{ job.company.charAt(0) }}
      </div>
      <span @click.stop="toggleBookmark"
        class="material-symbols-outlined text-outline group-hover:text-primary transition-colors cursor-pointer"
        :class="isBookmarked ? 'fill-icon text-primary' : ''">
        bookmark
      </span>
    </div>
    <h3 class="font-headline-sm text-headline-sm text-primary mb-1">{{ job.title }}</h3>
    <p class="font-body-md text-on-surface-variant mb-4">{{ job.company }}</p>
    <div class="flex flex-wrap gap-2 mb-6">
      <span v-if="matchScore !== undefined"
        class="px-2 py-1 bg-secondary-container/50 text-on-secondary-container text-[10px] font-bold rounded uppercase tracking-wider">
        {{ matchScore }}% Match
      </span>
      <span v-if="job.job_type"
        class="px-2 py-1 bg-surface-container text-on-surface-variant text-[10px] font-bold rounded uppercase tracking-wider">
        {{ job.job_type }}
      </span>
    </div>
    <div class="flex items-center justify-between pt-4 border-t border-outline-variant">
      <div class="flex items-center gap-1 text-on-surface-variant">
        <span class="material-symbols-outlined text-sm">location_on</span>
        <span class="text-label-sm">{{ job.location }}</span>
      </div>
      <p v-if="job.salary" class="text-label-sm font-semibold text-secondary">{{ job.salary }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  job: Object,
  matchScore: Number
})

const bookmarks = ref(JSON.parse(localStorage.getItem('geohire_bookmarks') || '[]'))

const isBookmarked = computed(() => bookmarks.value.includes(props.job.id))

function toggleBookmark() {
  const idx = bookmarks.value.indexOf(props.job.id)
  if (idx > -1) {
    bookmarks.value.splice(idx, 1)
  } else {
    bookmarks.value.push(props.job.id)
  }
  localStorage.setItem('geohire_bookmarks', JSON.stringify(bookmarks.value))
}
</script>

<style scoped>
.fill-icon {
  font-variation-settings: 'FILL' 1;
}
</style>
