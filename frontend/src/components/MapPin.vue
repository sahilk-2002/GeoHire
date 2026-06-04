<template>
  <l-marker :lat-lng="[job.latitude || 0, job.longitude || 0]" @click="emitClick">
    <l-tooltip>
      <div class="text-left min-w-[180px] max-w-[260px]">
        <div class="font-semibold text-sm mb-0.5">{{ job.title }}</div>
        <div class="text-xs text-on-surface-variant mb-1">{{ job.company }} &middot; {{ job.location }}</div>
        <div v-if="salaryText" class="text-xs font-semibold text-primary mb-1">{{ salaryText }}</div>
        <div v-if="job.description" class="text-xs text-on-surface-variant line-clamp-2 mb-1.5">{{ job.description }}</div>
        <div class="text-xs text-primary font-semibold underline">View Details &rarr;</div>
      </div>
    </l-tooltip>
  </l-marker>
</template>

<script setup>
import { computed } from 'vue'
import { LMarker, LTooltip } from '@vue-leaflet/vue-leaflet'
import { formatSalary } from '../utils/salary.js'

const props = defineProps({ job: Object })
const emit = defineEmits(['pin-click'])

const salaryText = computed(() => formatSalary(props.job))

function emitClick() {
  emit('pin-click', props.job)
}
</script>
