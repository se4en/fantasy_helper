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

httpClient.interceptors.response.use(
  response => response,
  error => {
    const { response } = error
    console.error("response error", error)
    return Promise.reject(error)
  }
)

export const ENDPOINTS = {
  LEAGUES_INFO: '/leagues_info/',
  COEFFS: '/coeffs/',
  CALENDAR: '/calendar/'
}

export default httpClient
