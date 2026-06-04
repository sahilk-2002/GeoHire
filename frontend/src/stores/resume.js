import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useResumeStore = defineStore('resume', () => {
  const resumeId = ref(null)
  const profile = ref(null)
  const uploading = ref(false)
  const error = ref('')

  async function uploadResume(file) {
    uploading.value = true
    error.value = ''
    resumeId.value = null
    profile.value = null
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch('/api/upload-resume', { method: 'POST', body: formData })
      if (!res.ok) {
        const msg = await res.text()
        throw new Error(msg || 'Upload failed')
      }
      const data = await res.json()
      resumeId.value = data.id
      profile.value = data.profile
    } catch (e) {
      resumeId.value = null
      profile.value = null
      error.value = e.message || 'Failed to parse resume. Try a different file format.'
    } finally {
      uploading.value = false
    }
  }

  function clear() {
    resumeId.value = null
    profile.value = null
    error.value = ''
  }

  return { resumeId, profile, uploading, error, uploadResume, clear }
})
