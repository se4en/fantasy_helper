import axios from 'axios'

const httpClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
})

httpClient.interceptors.request.use(config => {
  console.warn("VITE_API_URL", import.meta.env.VITE_API_URL)
  console.warn("config.baseUR", config.baseURL)
  console.warn("config.url", config.url)
  return config
})

// Add request interceptor
// httpClient.interceptors.request.use(config => {
//   if (!config.url.startsWith('http')) {
//     config.url = window.location.origin + config.url;
//   }
//   return config;
// });

httpClient.interceptors.response.use(
  response => response,
  error => {
    const { response } = error
    // console.error("response error", error)
    return Promise.reject(error)
  }
)

export const ENDPOINTS = {
  LEAGUES_INFO: '/leagues_info/',
  COEFFS: '/coeffs/',
  PLAYERS_STATS_INFO: '/players_stats_info/',
  CALENDAR: '/calendar/',
  ME: '/me',
  LOGOUT: '/logout'
}

export default httpClient
