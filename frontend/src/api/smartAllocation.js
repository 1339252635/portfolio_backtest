import api from './index'

/**
 * Smart Allocation API
 */

/**
 * Get risk assessment questions
 */
export function getRiskQuestions() {
  return api.get('/smart-allocation/risk-questions')
}

/**
 * Submit risk assessment and get allocation recommendation
 * @param {Object} data - Risk assessment data
 */
export function assessRisk(data) {
  return api.post('/smart-allocation/assess', data)
}

/**
 * Get all allocation templates
 */
export function getAllocationTemplates() {
  return api.get('/smart-allocation/templates')
}

/**
 * Adjust allocation based on market condition
 * @param {Object} data - Adjustment parameters
 */
export function adjustByMarket(data) {
  return api.post('/smart-allocation/adjust-by-market', data)
}
