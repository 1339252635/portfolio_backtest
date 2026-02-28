import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.error || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// 产品管理 API
export const productApi = {
  getList: (params) => api.get('/products', { params }),
  getById: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
  getData: (code, params) => api.get(`/products/${code}/data`, { params }),
  sync: (codes) => api.post('/products/sync', { codes }),
  initDefaults: () => api.post('/products/init-defaults')
}

// 回测 API
export const backtestApi = {
  getList: (params) => api.get('/backtest', { params }),
  getById: (id) => api.get(`/backtest/${id}`),
  create: (data) => api.post('/backtest', data),
  delete: (id) => api.delete(`/backtest/${id}`),
  getResults: (id) => api.get(`/backtest/${id}/results`),
  getMetrics: (id) => api.get(`/backtest/${id}/metrics`),
  getHoldings: (id, params) => api.get(`/backtest/${id}/holdings`, { params })
}

// 分析 API
export const analysisApi = {
  compare: (scenarioIds) => api.post('/analysis/compare', { scenario_ids: scenarioIds }),
  monteCarlo: (scenarioId, params) => api.post('/analysis/monte-carlo', { 
    scenario_id: scenarioId, 
    ...params 
  }),
  correlation: (data) => api.post('/analysis/correlation', data)
}

export default api
