// src/middleware/authGuard.js
import { API_BASE_URL } from '../config'

export async function checkAdminStatus() {
  try {
    const token = localStorage.getItem('token')
    if (!token) return false

    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (!response.ok) return false

    const userData = await response.json()
    return userData.is_superuser
  } catch (error) {
    console.error('Error checking admin status:', error)
    return false
  }
}