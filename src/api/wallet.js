import axios from 'axios'

const api = axios.create({
  baseURL: '/api/wallet',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add request interceptor to inject token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default {
  getBalance() {
    return api.get('/balance')
  },
  deposit(amount) {
    return api.post('/deposit', { amount })
  },
  withdraw(data) {
    return api.post('/withdraw', data)
  },
  getTransactions(page = 1) {
    return api.get('/transactions', { params: { page } })
  }
}
