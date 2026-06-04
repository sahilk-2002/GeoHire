<template>
  <div class="bg-primary-container text-on-primary-container p-lg rounded-xl shadow-lg relative overflow-hidden">
    <div class="absolute -right-12 -top-12 w-48 h-48 bg-white/10 rounded-full blur-3xl"></div>
    <div class="relative z-10">
      <div class="flex items-center gap-sm mb-md">
        <span class="material-symbols-outlined" style="fontVariationSettings: &quot;'FILL' 1&quot;">auto_awesome</span>
        <h2 class="font-headline-sm">Why you match</h2>
      </div>
      <p class="font-body-md text-body-md text-on-primary-container/90 mb-lg">
        Based on your uploaded resume, you have a <strong>{{ score }}%</strong> compatibility score for this role.
      </p>
      <div class="flex flex-wrap gap-sm">
        <div v-for="skill in skills" :key="skill"
          class="bg-white/20 backdrop-blur-sm border border-white/30 px-md py-2 rounded-lg flex items-center gap-sm">
          <span class="material-symbols-outlined text-[20px]" style="fontVariationSettings: &quot;'FILL' 1&quot;">check_circle</span>
          <span class="font-label-md text-label-md">{{ skill }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  score: { type: Number, default: 0 },
  skills: { type: Array, default: () => [] }
})
</script>
