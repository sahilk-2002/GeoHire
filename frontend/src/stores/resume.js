import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

const STORAGE_KEY = 'geohire_resume'

function loadFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch { return null }
}

function saveToStorage(data) {
  try {
    if (data) localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
    else localStorage.removeItem(STORAGE_KEY)
  } catch { /* quota exceeded */ }
}

export const useResumeStore = defineStore('resume', () => {
  const stored = loadFromStorage()
  const resumeId = ref(stored?.resumeId || null)
  const profile = ref(stored?.profile || null)
  const uploading = ref(false)
  const uploadError = ref('')

  function persist() {
    if (profile.value) {
      saveToStorage({ resumeId: resumeId.value, profile: profile.value })
    } else {
      saveToStorage(null)
    }
  }

  watch([resumeId, profile], persist, { deep: true })

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
