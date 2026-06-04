<template>
  <l-marker :lat-lng="[job.latitude || 0, job.longitude || 0]" :icon="pinIcon" @click="emitClick">
    <l-tooltip>
      <div class="text-center">
        <div class="text-sm font-semibold">{{ job.title }}</div>
        <div class="text-xs text-on-surface-variant">{{ job.company }} &bull; {{ job.location }}</div>
        <div v-if="job.salary" class="text-xs font-semibold text-primary mt-1">{{ job.salary }}</div>
      </div>
    </l-tooltip>
  </l-marker>
</template>

<script setup>
import { computed } from 'vue'
import { LMarker, LTooltip } from '@vue-leaflet/vue-leaflet'
import L from 'leaflet'

const props = defineProps({ job: Object })
const emit = defineEmits(['pin-click'])

const pinIcon = computed(() => {
  const initial = (props.job.company || '?').charAt(0).toUpperCase()
  const salary = props.job.salary || ''
  return L.divIcon({
    className: 'custom-job-pin',
    html: `<div class="pin-container">
      <div class="pin-circle">${initial}</div>
      ${salary ? `<div class="pin-salary">${salary}</div>` : ''}
    </div>`,
    iconSize: [40, 50],
    iconAnchor: [20, 50],
    popupAnchor: [0, -50],
  })
})

function emitClick() {
  emit('pin-click', props.job)
}
</script>
