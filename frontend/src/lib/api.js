const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1'

import axios from 'axios'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
})

// Attach token if present
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default client
