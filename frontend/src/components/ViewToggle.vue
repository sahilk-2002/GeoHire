<template>
  <div class="bg-surface-container-high p-1 rounded-full flex items-center">
    <button @click="$emit('toggle', 'list')"
      class="px-6 py-1.5 rounded-full font-label-sm transition-all duration-200"
      :class="view === 'list'
        ? 'bg-secondary-container text-on-secondary-container shadow-sm'
        : 'text-on-surface-variant hover:bg-surface-variant'">
      List View
    </button>
    <button @click="$emit('toggle', 'map')"
      class="px-6 py-1.5 rounded-full font-label-sm transition-all duration-200"
      :class="view === 'map'
        ? 'bg-secondary-container text-on-secondary-container shadow-sm'
        : 'text-on-surface-variant hover:bg-surface-variant'">
      Map View
    </button>
  </div>
</template>

<script setup>
defineProps({ view: { type: String, default: 'list' } })
defineEmits(['toggle'])
</script>
