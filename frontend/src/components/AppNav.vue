<template>
  <!-- Mobile bottom nav -->
  <nav class="fixed bottom-0 left-0 w-full z-50 flex lg:hidden justify-around items-center px-4 pb-4 pt-2 shadow-[0_-4px_12px_rgba(0,0,0,0.15)] bg-surface">
    <router-link v-for="item in items" :key="item.path" :to="item.path"
      class="flex flex-col items-center justify-center px-4 py-1 rounded-full transition-all duration-150 active:scale-90"
      :class="$route.path === item.path
        ? 'bg-secondary-container text-on-secondary-container'
        : 'text-on-surface-variant hover:bg-surface-container-high'">
      <span class="material-symbols-outlined text-sm" :style="$route.path === item.path ? &quot;font-variation-settings: 'FILL' 1&quot; : {}">{{ item.icon }}</span>
      <span class="font-label-sm text-label-sm">{{ item.label }}</span>
    </router-link>
  </nav>

  <!-- Desktop sidebar -->
  <aside class="hidden lg:flex fixed left-0 top-0 h-screen w-64 flex-col bg-surface border-r border-outline-variant z-50">
    <div class="flex items-center gap-3 px-6 py-6 border-b border-outline-variant/50">
      <span class="material-symbols-outlined text-primary text-2xl">explore</span>
      <span class="font-headline-md text-headline-md font-bold text-primary">GeoHire</span>
    </div>
    <nav class="flex-1 flex flex-col gap-1 px-3 py-4">
      <router-link v-for="item in items" :key="item.path" :to="item.path"
        class="flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-150 font-label-md text-label-md"
        :class="$route.path === item.path
          ? 'bg-primary text-on-primary shadow-sm'
          : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'">
        <span class="material-symbols-outlined" :style="$route.path === item.path ? &quot;font-variation-settings: 'FILL' 1&quot; : {}">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>
    <div class="px-6 py-4 border-t border-outline-variant/50">
      <p class="text-label-sm text-outline">&copy; GeoHire 2026</p>
    </div>
  </aside>
</template>

<script setup>
const items = [
  { path: '/', icon: 'work', label: 'Jobs' },
  { path: '/map', icon: 'map', label: 'Map' },
  { path: '/upload', icon: 'upload_file', label: 'Upload' },
  { path: '/profile', icon: 'person', label: 'Profile' },
]
</script>
