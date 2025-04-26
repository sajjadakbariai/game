import axios from 'axios'

const api = axios.create({
  baseURL: '/api/auth',
  headers: {
    'Content-Type': 'application/json'
  }
})

export default {
  login(credentials) {
    return api.post('/login', credentials)
  },
  register(userData) {
    return api.post('/register', userData)
  },
  logout() {
    return api.post('/logout')
  },
  getUser() {
    return api.get('/user')
  },
  forgotPassword(email) {
    return api.post('/forgot-password', { email })
  },
  resetPassword(data) {
    return api.post('/reset-password', data)
  }
}
