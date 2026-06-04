import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useResumeStore = defineStore('resume', () => {
  const resumeId = ref(null)
  const profile = ref(null)
  const uploading = ref(false)

  async function uploadResume(file) {
    uploading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch('/api/upload-resume', { method: 'POST', body: formData })
      const data = await res.json()
      resumeId.value = data.id
      profile.value = data.profile
    } catch {
      resumeId.value = null
      profile.value = null
    } finally {
      uploading.value = false
    }
  }

  function clear() {
    resumeId.value = null
    profile.value = null
  }

  return { resumeId, profile, uploading, uploadResume, clear }
})
