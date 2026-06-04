<template>
  <section class="mb-lg">
    <div class="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant p-4 flex flex-col md:flex-row gap-4">
      <div class="flex-1 flex items-center gap-3 bg-surface-container-low px-4 py-3 rounded-lg border border-transparent focus-within:border-primary transition-colors">
        <span class="material-symbols-outlined text-outline">work</span>
        <input v-model="titleQuery" @keyup.enter="$emit('search', titleQuery, locationQuery)"
          class="bg-transparent border-none focus:ring-0 w-full font-body-md text-on-surface placeholder:text-outline p-0 outline-none"
          placeholder="Job title or keywords" type="text" />
      </div>
      <div class="flex-1 flex items-center gap-3 bg-surface-container-low px-4 py-3 rounded-lg border border-transparent focus-within:border-primary transition-colors">
        <span class="material-symbols-outlined text-outline">location_on</span>
        <input v-model="locationQuery" @keyup.enter="$emit('search', titleQuery, locationQuery)"
          class="bg-transparent border-none focus:ring-0 w-full font-body-md text-on-surface placeholder:text-outline p-0 outline-none"
          placeholder="Location" type="text" />
      </div>
      <button @click="$emit('search', titleQuery, locationQuery)"
        class="bg-primary hover:opacity-90 text-on-primary px-8 py-3 rounded-lg font-label-md transition-all active:scale-95">
        Search
      </button>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'

defineEmits(['search'])
const titleQuery = ref('')
const locationQuery = ref('')
</script>
