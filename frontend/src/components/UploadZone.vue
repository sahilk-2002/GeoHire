<template>
  <div @click="$refs.input.click()" @dragover.prevent @drop.prevent="handleDrop"
    class="border-2 border-dashed border-outline-variant bg-surface-container-lowest rounded-xl p-xl flex flex-col items-center justify-center transition-all duration-300 hover:border-primary cursor-pointer active:scale-[0.98]"
    :class="{ 'border-primary bg-surface-container': isDragging }">
    <div class="w-20 h-20 rounded-full bg-surface-container flex items-center justify-center mb-md">
      <span class="material-symbols-outlined text-primary text-[40px]">upload_file</span>
    </div>
    <h2 class="font-headline-sm text-headline-sm text-on-surface mb-xs">Drop your resume here</h2>
    <p class="font-body-sm text-body-sm text-on-surface-variant mb-lg">PDF, DOCX up to 10MB</p>
    <button type="button" class="bg-primary text-on-primary px-lg py-sm rounded-lg font-label-md text-label-md shadow-lg active:scale-95 transition-transform">
      Browse Files
    </button>
    <input ref="input" type="file" accept=".pdf,.docx" class="hidden" @change="handleFile" />
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['file-selected'])
const isDragging = ref(false)
const input = ref(null)

function handleFile(e) {
  const file = e.target.files?.[0]
  if (file) emit('file-selected', file)
}

function handleDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) emit('file-selected', file)
}
</script>
