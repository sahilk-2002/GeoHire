<template>
  <div class="min-h-screen bg-background lg:pl-64">
    <router-view />
    <AppNav />
    <HomeLocationModal v-if="showHomeModal" @confirm="onHomeConfirm" @skip="onHomeSkip" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AppNav from './components/AppNav.vue'
import HomeLocationModal from './components/HomeLocationModal.vue'
import { useResumeStore } from './stores/resume'

const resumeStore = useResumeStore()
const showHomeModal = ref(false)

onMounted(() => {
  if (resumeStore.homeLatitude == null && !localStorage.getItem('geohire_home_skipped')) {
    showHomeModal.value = true
  }
})

function onHomeConfirm(lat, lng) {
  resumeStore.setHomeLocation(lat, lng)
  showHomeModal.value = false
}

function onHomeSkip() {
  localStorage.setItem('geohire_home_skipped', '1')
  showHomeModal.value = false
}
</script>
