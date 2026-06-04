<template>
  <div class="min-h-screen bg-background">
    <router-view />
    <AppNav />
  </div>
</template>

<script setup>
import AppNav from './components/AppNav.vue'
</script>
