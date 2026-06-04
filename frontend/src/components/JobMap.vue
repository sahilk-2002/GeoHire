<template>
  <div class="h-full w-full rounded-2xl overflow-hidden shadow-lg border border-outline-variant relative">
    <l-map :zoom="zoom" :center="center" :useGlobalLeaflet="false" @update:center="emitCenter" @update:zoom="emitZoom" style="height: 100%; width: 100%;">
      <l-tile-layer :url="tileUrl" :attribution="attribution" />
      <MapPin v-for="job in jobs" :key="job.id" :job="job" @pin-click="(j) => $emit('pin-click', j)" />
    </l-map>
  </div>
</template>

<script setup>
import { LMap, LTileLayer } from '@vue-leaflet/vue-leaflet'
import MapPin from './MapPin.vue'

const props = defineProps({
  jobs: { type: Array, default: () => [] },
  center: { type: Array, default: () => [20, 0] },
  zoom: { type: Number, default: 2 }
})

const emit = defineEmits(['update:center', 'update:zoom', 'pin-click'])
const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'

function emitCenter(c) { emit('update:center', c) }
function emitZoom(z) { emit('update:zoom', z) }
</script>
