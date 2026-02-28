import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { backtestApi } from '@/api'

export const useBacktestStore = defineStore('backtest', () => {
  // State
  const scenarios = ref([])
  const currentScenario = ref(null)
  const currentResults = ref([])
  const currentMetrics = ref(null)
  const loading = ref(false)

  // Getters
  const scenarioList = computed(() => scenarios.value)

  // Actions
  const fetchBacktestList = async (params = {}) => {
    loading.value = true
    try {
      const response = await backtestApi.getList(params)
      scenarios.value = response.items || []
      return response.items || []
    } catch (error) {
      console.error('Failed to fetch scenarios:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createBacktest = async (data) => {
    loading.value = true
    try {
      const response = await backtestApi.create(data)
      if (response.scenario) {
        scenarios.value.unshift(response.scenario)
      }
      return response.scenario || response
    } catch (error) {
      console.error('Failed to create scenario:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const deleteBacktest = async (id) => {
    await backtestApi.delete(id)
    scenarios.value = scenarios.value.filter(s => s.id !== id)
  }

  const fetchBacktestResult = async (id) => {
    loading.value = true
    try {
      const [scenarioRes, metricsRes, holdingsRes] = await Promise.all([
        backtestApi.getById(id),
        backtestApi.getMetrics(id),
        backtestApi.getHoldings(id)
      ])
      return {
        scenario: scenarioRes.scenario || scenarioRes,
        metrics: metricsRes.metrics || metricsRes,
        holdings: holdingsRes.holdings || holdingsRes || [],
        daily_values: holdingsRes.daily_values || []
      }
    } catch (error) {
      console.error('Failed to fetch result:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  // 保留原有方法以兼容
  const fetchScenarios = fetchBacktestList
  const createScenario = createBacktest
  const deleteScenario = deleteBacktest
  const fetchResults = fetchBacktestResult
  const fetchMetrics = async (id) => {
    const response = await backtestApi.getMetrics(id)
    currentMetrics.value = response.metrics
    return response
  }

  return {
    scenarios,
    currentScenario,
    currentResults,
    currentMetrics,
    loading,
    scenarioList,
    fetchBacktestList,
    createBacktest,
    deleteBacktest,
    fetchBacktestResult,
    fetchScenarios,
    createScenario,
    deleteScenario,
    fetchResults,
    fetchMetrics
  }
})
