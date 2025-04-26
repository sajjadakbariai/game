import axios from 'axios'

const api = axios.create({
  baseURL: '/api/games',
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default {
  getGameList() {
    return api.get('/')
  },
  // Crash Game
  placeCrashBet(data) {
    return api.post('/crash/bet', data)
  },
  cashOutCrash(gameId) {
    return api.post(`/crash/${gameId}/cashout`)
  },
  getCrashHistory() {
    return api.get('/crash/history')
  },
  // Hokm Game
  createHokmRoom(data) {
    return api.post('/hokm/create', data)
  },
  joinHokmRoom(roomId) {
    return api.post(`/hokm/${roomId}/join`)
  },
  // Poker Game
  createPokerRoom(data) {
    return api.post('/poker/create', data)
  },
  joinPokerRoom(roomId) {
    return api.post(`/poker/${roomId}/join`)
  }
}
