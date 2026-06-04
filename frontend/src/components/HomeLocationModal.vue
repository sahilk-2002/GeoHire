<template>
  <div class="fixed inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
    <div class="bg-surface-container-lowest rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] flex flex-col overflow-hidden">
      <div class="p-5 border-b border-outline-variant/50">
        <h2 class="font-headline-md text-headline-md text-on-surface font-bold">Set Your Home Location</h2>
        <p class="text-sm text-on-surface-variant mt-1">Click on the map to drop a red pin at your home. This helps us calculate commute routes to jobs.</p>
      </div>
      <div class="flex-1 min-h-[300px] relative">
        <l-map ref="mapRef" :zoom="4" :center="center" :useGlobalLeaflet="false" :options="mapOptions"
          @ready="onMapReady"
          style="height: 350px; width: 100%;">
          <l-tile-layer :url="tileUrl" :attribution="attribution" />
          <l-marker v-if="selectedLat != null" :lat-lng="[selectedLat, selectedLng]"
            :icon="homeIcon" />
        </l-map>
      </div>
      <div class="p-5 border-t border-outline-variant/50 flex items-center justify-between gap-3">
        <button @click="skip" class="text-on-surface-variant text-sm hover:underline">Skip for now</button>
        <button @click="confirm"
          :disabled="selectedLat == null"
          class="bg-primary text-on-primary px-6 py-2.5 rounded-lg font-label-md disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-90 transition-opacity">
          Confirm Location
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { LMap, LTileLayer, LMarker } from '@vue-leaflet/vue-leaflet'
import L from 'leaflet'

const emit = defineEmits(['confirm', 'skip'])

const mapRef = ref(null)
const center = ref([20, 78])
const mapOptions = { zoomControl: false }
const selectedLat = ref(null)
const selectedLng = ref(null)
const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'

const homeIcon = L.divIcon({
  html: '<span class="material-symbols-outlined text-3xl" style="color:#dc2626;filter:drop-shadow(0 0 4px rgba(0,0,0,0.5))">home_pin</span>',
  className: '',
  iconSize: [32, 32],
  iconAnchor: [16, 32],
})

function onMapReady(map) {
  map.on('click', (e) => {
    selectedLat.value = e.latlng.lat
    selectedLng.value = e.latlng.lng
  })
}

function confirm() {
  if (selectedLat.value != null) {
    emit('confirm', selectedLat.value, selectedLng.value)
  }
}

function skip() {
  emit('skip')
}
</script>
