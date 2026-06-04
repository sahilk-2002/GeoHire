<template>
  <div class="h-full w-full rounded-2xl overflow-hidden shadow-lg border border-outline-variant relative">
    <l-map ref="mapRef" :zoom="zoom" :center="center" :useGlobalLeaflet="false" :options="mapOptions"
      @ready="onMapReady"
      @update:center="emitCenter" @update:zoom="emitZoom"
      style="height: 100%; width: 100%; cursor: default;">
      <l-tile-layer :url="tileUrl" :attribution="attribution" />
      <MapPin v-for="job in jobs" :key="job.id" :job="job" @pin-click="(j) => $emit('pin-click', j)" />
    </l-map>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { LMap, LTileLayer } from '@vue-leaflet/vue-leaflet'
import L from 'leaflet'
import MapPin from './MapPin.vue'

const props = defineProps({
  jobs: { type: Array, default: () => [] },
  center: { type: Array, default: () => [20, 0] },
  zoom: { type: Number, default: 2 },
  drawActive: { type: Boolean, default: false },
  cleared: { type: Number, default: 0 },
  routeTo: { type: Object, default: null },
  homeLat: { type: Number, default: null },
  homeLng: { type: Number, default: null },
})

const emit = defineEmits(['update:center', 'update:zoom', 'pin-click', 'area-drawn'])

const mapRef = ref(null)
const mapOptions = { zoomControl: false }
let leafletMap = null
let rectangle = null
let startLatLng = null
let tempRect = null
let drawListeners = []
let routeGroup = null
let homeMarker = null

const tileUrl = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'

watch(() => props.cleared, () => { removeRect() })

watch(() => props.drawActive, (active) => {
  if (!active) removeRect()
})

watch([() => props.routeTo, () => props.homeLat, () => props.homeLng], () => {
  clearRoute()
  if (props.routeTo && props.homeLat != null) {
    drawRoute()
  }
})

function onMapReady(map) {
  leafletMap = map
  leafletMap.on('mousedown', onMouseDown)
  leafletMap.on('mousemove', onMouseMove)
  leafletMap.on('mouseup', onMouseUp)
  drawListeners = [leafletMap]
  routeGroup = L.layerGroup().addTo(leafletMap)
  homeMarker = L.marker([0, 0], {
    icon: L.divIcon({
      html: '<span class="material-symbols-outlined text-3xl" style="color:#dc2626;filter:drop-shadow(0 0 4px rgba(0,0,0,0.5))">home_pin</span>',
      className: '',
      iconSize: [32, 32],
      iconAnchor: [16, 32],
    }),
    interactive: false,
  })
}

onUnmounted(() => {
  drawListeners.forEach(m => m.off())
  drawListeners = []
})

function removeRect() {
  if (rectangle) { leafletMap?.removeLayer(rectangle); rectangle = null }
  if (tempRect) { leafletMap?.removeLayer(tempRect); tempRect = null }
  startLatLng = null
}

function clearRoute() {
  if (!routeGroup) return
  routeGroup.clearLayers()
}

async function drawRoute() {
  const fromLng = props.homeLng
  const fromLat = props.homeLat
  const toLng = props.routeTo.lng
  const toLat = props.routeTo.lat

  if (!routeGroup) return

  const home = L.marker([fromLat, fromLng], {
    icon: L.divIcon({
      html: '<span class="material-symbols-outlined text-3xl" style="color:#dc2626;filter:drop-shadow(0 0 4px rgba(0,0,0,0.5))">home_pin</span>',
      className: '',
      iconSize: [32, 32],
      iconAnchor: [16, 32],
    }),
    interactive: false,
  })
  routeGroup.addLayer(home)

  const dest = L.marker([toLat, toLng], {
    icon: L.divIcon({
      html: '<span class="material-symbols-outlined text-3xl" style="color:#2563eb;filter:drop-shadow(0 0 4px rgba(0,0,0,0.5))">location_on</span>',
      className: '',
      iconSize: [32, 32],
      iconAnchor: [16, 32],
    }),
    interactive: false,
  })
  routeGroup.addLayer(dest)

  try {
    const url = `https://router.project-osrm.org/route/v1/driving/${fromLng},${fromLat};${toLng},${toLat}?geometries=geojson&overview=full`
    const res = await fetch(url)
    const data = await res.json()
    if (data.code !== 'Ok' || !data.routes?.length) {
      drawFallbackLine(fromLat, fromLng, toLat, toLng)
      return
    }
    const coords = data.routes[0].geometry.coordinates.map(c => [c[1], c[0]])
    const polyline = L.polyline(coords, {
      color: '#4f46e5', weight: 4, opacity: 0.8,
    })
    routeGroup.addLayer(polyline)

    const dist = (data.routes[0].distance / 1000).toFixed(1)
    const dur = Math.round(data.routes[0].duration / 60)
    const mid = coords[Math.floor(coords.length / 2)]
    const label = L.marker(mid, {
      icon: L.divIcon({
        html: `<div class="bg-white px-2 py-1 rounded-full shadow text-xs font-semibold whitespace-nowrap border border-outline-variant">${dist} km · ${dur} min</div>`,
        className: '',
        iconSize: [0, 0],
        iconAnchor: [0, 0],
      }),
      interactive: false,
    })
    routeGroup.addLayer(label)

    leafletMap.fitBounds(polyline.getBounds(), { padding: [60, 60] })
  } catch {
    drawFallbackLine(fromLat, fromLng, toLat, toLng)
  }
}

function drawFallbackLine(fromLat, fromLng, toLat, toLng) {
  const line = L.polyline([[fromLat, fromLng], [toLat, toLng]], {
    color: '#4f46e5', weight: 2, opacity: 0.5, dashArray: '8,6',
  })
  routeGroup.addLayer(line)
  leafletMap.fitBounds(line.getBounds(), { padding: [60, 60] })
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
