import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'JobDiscovery', component: () => import('../views/JobDiscovery.vue') },
  { path: '/jobs/:id', name: 'JobDetails', component: () => import('../views/JobDetails.vue') },
  { path: '/upload', name: 'ResumeUpload', component: () => import('../views/ResumeUpload.vue') },
  { path: '/map', name: 'MapView', component: () => import('../views/MapView.vue') },
  { path: '/profile', name: 'Profile', component: () => import('../views/Profile.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
