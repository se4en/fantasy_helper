import axios from 'axios'

const httpClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000
})

httpClient.interceptors.request.use(config => {
  console.error("VITE_API_URL", import.meta.env.VITE_API_URL)
  console.error("request full url", config.baseURL, config.url)
  return config
})

// Response interceptor
httpClient.interceptors.response.use(
  response => response,
  error => {
    const { response } = error
    // if (response?.status === 401) {
    //   window.location.href = '/login' // Redirect to login
    // }
    console.error("response error", error)
    return Promise.reject(error)
  }
)


export const ENDPOINTS = {
  LEAGUES_INFO: '/leagues_info/'
}

export default httpClient

