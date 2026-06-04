<template>
  <nav class="fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 pb-4 pt-2 bg-surface shadow-lg rounded-t-xl">
    <router-link v-for="item in items" :key="item.path" :to="item.path"
      class="flex flex-col items-center justify-center px-4 py-1 rounded-full transition-all duration-150 active:scale-90"
      :class="$route.path === item.path
        ? 'bg-secondary-container text-on-secondary-container'
        : 'text-on-surface-variant hover:bg-surface-container-high'">
      <span class="material-symbols-outlined text-sm">{{ item.icon }}</span>
      <span class="font-label-sm text-label-sm">{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
const items = [
  { path: '/', icon: 'work', label: 'Jobs' },
  { path: '/map', icon: 'map', label: 'Map' },
  { path: '/upload', icon: 'upload_file', label: 'Upload' },
  { path: '/profile', icon: 'person', label: 'Profile' },
]
</script>
