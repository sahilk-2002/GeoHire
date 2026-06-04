import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useResumeStore = defineStore('resume', () => {
  const resumeId = ref(null)
  const profile = ref(null)
  const uploading = ref(false)
  const uploadError = ref('')

  async function uploadResume(file) {
    uploading.value = true
    uploadError.value = ''
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await fetch('/api/upload-resume', { method: 'POST', body: formData })
      const data = await res.json()
      if (!res.ok) {
        throw new Error(data.detail || `Upload failed (${res.status})`)
      }
      resumeId.value = data.id
      profile.value = data.profile
    } catch (err) {
      resumeId.value = null
      profile.value = null
      uploadError.value = err.message
    } finally {
      uploading.value = false
    }
  }

  function updateProfile(updated) {
    profile.value = { ...profile.value, ...updated }
  }

  function clear() {
    resumeId.value = null
    profile.value = null
    uploadError.value = ''
  }

  return { resumeId, profile, uploading, uploadError, uploadResume, updateProfile, clear }
})
