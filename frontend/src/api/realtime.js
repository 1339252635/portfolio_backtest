import api from './index'

/**
 * Realtime Market Data API
 */

/**
 * Get realtime quote for a single product
 * @param {string} code - Product code
 */
export function getRealtimeQuote(code) {
  return api.get(`/realtime/quote/${code}`)
}

/**
 * Get batch realtime quotes
 * @param {string[]} codes - Array of product codes
 */
export function getBatchQuotes(codes) {
  return api.post('/realtime/quotes', { codes })
}

/**
 * Get realtime data for all products
 */
export function getAllProductsRealtime() {
  return api.get('/realtime/products')
}

/**
 * Get market overview (major indices)
 */
export function getMarketOverview() {
  return api.get('/realtime/market-overview')
}

/**
 * Subscribe to realtime updates
 * @param {string[]} codes - Array of product codes to subscribe
 */
export function subscribeRealtime(codes) {
  return api.post('/realtime/subscribe', { codes })
}
