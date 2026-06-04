<template>
  <div class="h-full w-full rounded-2xl overflow-hidden shadow-lg border border-outline-variant relative">
    <l-map ref="mapRef" :zoom="zoom" :center="center" :useGlobalLeaflet="false" :options="mapOptions"
      @update:center="emitCenter" @update:zoom="emitZoom"
      @mousedown="onMouseDown" @mousemove="onMouseMove" @mouseup="onMouseUp"
      style="height: 100%; width: 100%; cursor: default;">
      <l-tile-layer :url="tileUrl" :attribution="attribution" />
      <MapPin v-for="job in jobs" :key="job.id" :job="job" @pin-click="(j) => $emit('pin-click', j)" />
    </l-map>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { LMap, LTileLayer } from '@vue-leaflet/vue-leaflet'
import L from 'leaflet'
import MapPin from './MapPin.vue'

const props = defineProps({
  jobs: { type: Array, default: () => [] },
  center: { type: Array, default: () => [20, 0] },
  zoom: { type: Number, default: 2 },
  drawActive: { type: Boolean, default: false },
  cleared: { type: Number, default: 0 },
})

const emit = defineEmits(['update:center', 'update:zoom', 'pin-click', 'area-drawn'])

const mapRef = ref(null)
const mapOptions = { zoomControl: false }
let leafletMap = null
let rectangle = null
let startLatLng = null
let tempRect = null
let drawListeners = []

const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'

watch(() => props.cleared, () => { removeRect() })

watch(() => props.drawActive, (active) => {
  if (!active) removeRect()
})

onMounted(() => {
  leafletMap = mapRef.value?.leafletObject
  if (!leafletMap) return
  leafletMap.on('mousedown', onMouseDown)
  leafletMap.on('mousemove', onMouseMove)
  leafletMap.on('mouseup', onMouseUp)
  drawListeners = [leafletMap]
})

onUnmounted(() => {
  drawListeners.forEach(m => m.off())
  drawListeners = []
})

function removeRect() {
  if (rectangle) { leafletMap?.removeLayer(rectangle); rectangle = null }
  if (tempRect) { leafletMap?.removeLayer(tempRect); tempRect = null }
  startLatLng = null
}

function onMouseDown(e) {
  if (!props.drawActive) return
  removeRect()
  startLatLng = e.latlng
  tempRect = L.rectangle(L.latLngBounds(startLatLng, startLatLng), {
    color: '#4f46e5', weight: 2, fillOpacity: 0.1, dashArray: '6,4',
  }).addTo(leafletMap)
}

function onMouseMove(e) {
  if (!tempRect || !startLatLng) return
  const bounds = L.latLngBounds(startLatLng, e.latlng)
  tempRect.setBounds(bounds)
}

function onMouseUp() {
  if (!tempRect || !startLatLng) return
  const bounds = tempRect.getBounds()
  leafletMap?.removeLayer(tempRect)
  tempRect = null
  rectangle = L.rectangle(bounds, {
    color: '#4f46e5', weight: 2, fillOpacity: 0.15,
  }).addTo(leafletMap)
  startLatLng = null
  emit('area-drawn', {
    north: bounds.getNorth(), south: bounds.getSouth(),
    east: bounds.getEast(), west: bounds.getWest(),
  })
}

function emitCenter(c) { emit('update:center', c) }
function emitZoom(z) { emit('update:zoom', z) }
</script>
