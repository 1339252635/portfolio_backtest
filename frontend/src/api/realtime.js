import axios from 'axios'
import api from './index'

/**
 * Realtime Market Data API
 */

// 创建专门的实时数据API实例，使用更长的超时时间
const realtimeApi = axios.create({
  baseURL: '/api',
  timeout: 60000,  // 60秒超时
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * Get realtime quote for a single product
 * @param {string} code - Product code
 */
export function getRealtimeQuote(code) {
  return realtimeApi.get(`/realtime/quote/${code}`)
}

/**
 * Get batch realtime quotes
 * @param {string[]} codes - Array of product codes
 */
export function getBatchQuotes(codes) {
  return realtimeApi.post('/realtime/quotes', { codes })
}

/**
 * Get realtime data for all products
 */
export function getAllProductsRealtime() {
  return realtimeApi.get('/realtime/products')
}

/**
 * Get market overview (major indices)
 */
export function getMarketOverview() {
  return realtimeApi.get('/realtime/market-overview')
}

/**
 * Subscribe to realtime updates
 * @param {string[]} codes - Array of product codes to subscribe
 */
export function subscribeRealtime(codes) {
  return api.post('/realtime/subscribe', { codes })
}
