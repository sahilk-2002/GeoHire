<template>
  <div class="min-h-screen bg-background lg:pl-64">
    <router-view />
    <AppNav />
  </div>
</template>

<script setup>
import AppNav from './components/AppNav.vue'
</script>