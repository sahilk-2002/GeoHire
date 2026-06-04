<template>
  <l-marker :lat-lng="[job.latitude || 0, job.longitude || 0]" @click="emitClick">
    <l-tooltip>
      <div class="text-center">
        <div v-if="job.salary" class="text-xs font-semibold text-primary">{{ job.salary }}</div>
        <div class="text-sm font-semibold">{{ job.title }}</div>
        <div class="text-xs text-on-surface-variant">{{ job.company }}</div>
      </div>
    </l-tooltip>
  </l-marker>
</template>

<script setup>
import { LMarker, LTooltip } from '@vue-leaflet/vue-leaflet'

const props = defineProps({ job: Object })
const emit = defineEmits(['pin-click'])

function emitClick() {
  emit('pin-click', props.job)
}
</script>
