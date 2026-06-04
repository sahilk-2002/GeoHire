<template>
  <l-marker :lat-lng="[job.latitude || 0, job.longitude || 0]">
    <l-tooltip>
      <div class="text-sm font-semibold">{{ job.title }}</div>
      <div class="text-xs">{{ job.company }} - {{ job.salary || 'Salary N/A' }}</div>
    </l-tooltip>
  </l-marker>
</template>

<script setup>
import { LMarker, LTooltip } from '@vue-leaflet/vue-leaflet'

defineProps({ job: Object })
</script>
