import request from '@/utils/request'

/**
 * 智能配置建议 API
 */

/**
 * 获取风险评估问卷
 */
export function getRiskQuestions() {
  return request({
    url: '/smart-allocation/risk-questions',
    method: 'get'
  })
}

/**
 * 提交风险评估，获取配置建议
 * @param {Object} data - 风险评估数据
 */
export function assessRisk(data) {
  return request({
    url: '/smart-allocation/assess',
    method: 'post',
    data
  })
}

/**
 * 获取所有配置模板
 */
export function getAllocationTemplates() {
  return request({
    url: '/smart-allocation/templates',
    method: 'get'
  })
}

/**
 * 根据市场情况调整配置
 * @param {Object} data - 调整参数
 */
export function adjustByMarket(data) {
  return request({
    url: '/smart-allocation/adjust-by-market',
    method: 'post',
    data
  })
}
