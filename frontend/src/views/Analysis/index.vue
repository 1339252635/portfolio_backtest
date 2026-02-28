<template>
  <div class="analysis-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">数据分析</h1>
        <p class="page-subtitle">深度分析您的投资组合表现</p>
      </div>
    </div>

    <el-card class="apple-card">
      <el-tabs v-model="activeTab" class="apple-tabs">
        <!-- 方案对比 -->
        <el-tab-pane name="compare">
          <template #label>
            <div class="tab-label">
              <el-icon><ScaleToOriginal /></el-icon>
              <span>方案对比</span>
            </div>
          </template>
          <div class="tab-content">
            <div class="control-panel">
              <div class="control-group">
                <label class="control-label">选择要对比的方案</label>
                <el-select
                  v-model="compareForm.scenario_ids"
                  multiple
                  placeholder="选择方案"
                  class="apple-select"
                  popper-class="apple-select-dropdown"
                >
                  <el-option
                    v-for="scenario in backtestList"
                    :key="scenario.id"
                    :label="scenario.name"
                    :value="scenario.id"
                  />
                </el-select>
              </div>
              <button
                class="apple-btn primary"
                @click="compareScenarios"
                :disabled="compareForm.scenario_ids.length < 2"
              >
                <el-icon><TrendCharts /></el-icon>
                <span>开始对比</span>
              </button>
            </div>

            <div v-if="compareResult" class="result-panel">
              <div ref="compareChartRef" class="chart-container"></div>
            </div>

            <div v-else class="empty-state">
              <div class="empty-icon">
                <el-icon size="64" color="#c7c7cc"><ScaleToOriginal /></el-icon>
              </div>
              <h3>方案对比</h3>
              <p>选择至少两个回测方案进行对比分析</p>
            </div>
          </div>
        </el-tab-pane>

        <!-- 蒙特卡洛模拟 -->
        <el-tab-pane name="montecarlo">
          <template #label>
            <div class="tab-label">
              <el-icon><DataAnalysis /></el-icon>
              <span>蒙特卡洛模拟</span>
            </div>
          </template>
          <div class="tab-content">
            <div class="control-panel">
              <div class="control-row">
                <div class="control-group">
                  <label class="control-label">选择方案</label>
                  <el-select v-model="mcForm.scenario_id" placeholder="选择方案" class="apple-select">
                    <el-option
                      v-for="scenario in backtestList"
                      :key="scenario.id"
                      :label="scenario.name"
                      :value="scenario.id"
                    />
                  </el-select>
                </div>
                <div class="control-group">
                  <label class="control-label">模拟次数</label>
                  <el-input-number v-model="mcForm.simulations" :min="100" :max="10000" :step="100" class="apple-input-number" />
                </div>
                <div class="control-group">
                  <label class="control-label">预测年限</label>
                  <el-input-number v-model="mcForm.years" :min="1" :max="30" class="apple-input-number" />
                </div>
              </div>
              <button
                class="apple-btn primary"
                @click="runMonteCarlo"
                :disabled="!mcForm.scenario_id"
              >
                <el-icon><VideoPlay /></el-icon>
                <span>运行模拟</span>
              </button>
            </div>

            <div v-if="mcResult" class="result-panel">
              <div ref="mcChartRef" class="chart-container"></div>
            </div>

            <div v-else class="empty-state">
              <div class="empty-icon">
                <el-icon size="64" color="#c7c7cc"><DataAnalysis /></el-icon>
              </div>
              <h3>蒙特卡洛模拟</h3>
              <p>通过随机模拟预测投资组合的未来表现</p>
            </div>
          </div>
        </el-tab-pane>

        <!-- 相关性分析 -->
        <el-tab-pane name="correlation">
          <template #label>
            <div class="tab-label">
              <el-icon><Connection /></el-icon>
              <span>相关性分析</span>
            </div>
          </template>
          <div class="tab-content">
            <div class="control-panel">
              <div class="control-group">
                <label class="control-label">选择产品</label>
                <el-select
                  v-model="correlationForm.product_codes"
                  multiple
                  placeholder="选择产品"
                  class="apple-select"
                >
                  <el-option
                    v-for="product in productList"
                    :key="product.code"
                    :label="product.name"
                    :value="product.code"
                  />
                </el-select>
              </div>
              <button
                class="apple-btn primary"
                @click="analyzeCorrelation"
                :disabled="correlationForm.product_codes.length < 2"
              >
                <el-icon><TrendCharts /></el-icon>
                <span>分析相关性</span>
              </button>
            </div>

            <div v-if="correlationResult" class="result-panel">
              <div ref="correlationChartRef" class="chart-container"></div>
            </div>

            <div v-else class="empty-state">
              <div class="empty-icon">
                <el-icon size="64" color="#c7c7cc"><Connection /></el-icon>
              </div>
              <h3>相关性分析</h3>
              <p>选择至少两个产品分析它们之间的相关性</p>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { useBacktestStore } from '@/stores/backtest'
import { useProductsStore } from '@/stores/products'
import axios from 'axios'

const backtestStore = useBacktestStore()
const productsStore = useProductsStore()

const activeTab = ref('compare')
const backtestList = ref([])
const productList = ref([])

const compareForm = ref({
  scenario_ids: []
})
const compareResult = ref(null)
const compareChartRef = ref(null)

const mcForm = ref({
  scenario_id: null,
  simulations: 1000,
  years: 10
})
const mcResult = ref(null)
const mcChartRef = ref(null)

const correlationForm = ref({
  product_codes: []
})
const correlationResult = ref(null)
const correlationChartRef = ref(null)

let compareChart = null
let mcChart = null
let correlationChart = null

const fetchData = async () => {
  try {
    backtestList.value = await backtestStore.fetchBacktestList()
    productList.value = await productsStore.fetchProducts()
  } catch (error) {
    ElMessage.error('获取数据失败')
  }
}

const compareScenarios = async () => {
  if (compareForm.value.scenario_ids.length < 2) {
    ElMessage.warning('请至少选择两个方案进行对比')
    return
  }

  try {
    const response = await axios.post('/api/analysis/compare', {
      scenario_ids: compareForm.value.scenario_ids
    })
    compareResult.value = response.data

    nextTick(() => {
      initCompareChart(response.data)
    })
  } catch (error) {
    ElMessage.error('对比分析失败')
  }
}

const runMonteCarlo = async () => {
  if (!mcForm.value.scenario_id) {
    ElMessage.warning('请选择方案')
    return
  }

  try {
    const response = await axios.post('/api/analysis/monte-carlo', mcForm.value)
    mcResult.value = response.data

    nextTick(() => {
      initMCChart(response.data)
    })
  } catch (error) {
    ElMessage.error('蒙特卡洛模拟失败')
  }
}

const analyzeCorrelation = async () => {
  if (correlationForm.value.product_codes.length < 2) {
    ElMessage.warning('请至少选择两个产品')
    return
  }

  try {
    const response = await axios.post('/api/analysis/correlation', {
      product_codes: correlationForm.value.product_codes
    })
    correlationResult.value = response.data

    nextTick(() => {
      initCorrelationChart(response.data)
    })
  } catch (error) {
    ElMessage.error('相关性分析失败')
  }
}

const initCompareChart = (data) => {
  if (!compareChartRef.value) return

  if (compareChart) {
    compareChart.dispose()
  }

  compareChart = echarts.init(compareChartRef.value)

  const colors = ['#0071e3', '#34c759', '#ff9500', '#af52de', '#ff3b30', '#5ac8fa']

  const series = data.scenarios.map((scenario, index) => ({
    name: scenario.name,
    type: 'line',
    data: scenario.values,
    smooth: true,
    symbol: 'none',
    lineStyle: {
      width: 3,
      color: colors[index % colors.length]
    },
    itemStyle: {
      color: colors[index % colors.length]
    },
    areaStyle: {
      opacity: 0.1,
      color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
        { offset: 0, color: colors[index % colors.length] },
        { offset: 1, color: 'rgba(255,255,255,0)' }
      ])
    }
  }))

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(0, 0, 0, 0.05)',
      borderWidth: 1,
      textStyle: { color: '#1d1d1f' },
      padding: [12, 16]
    },
    legend: {
      data: data.scenarios.map(s => s.name),
      bottom: 0,
      itemGap: 24,
      textStyle: { color: '#86868b', fontSize: 13 }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.dates,
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.1)' } },
      axisLabel: { color: '#86868b', fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      name: '净值',
      nameTextStyle: { color: '#86868b' },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#86868b', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } }
    },
    series
  }

  compareChart.setOption(option)
}

const initMCChart = (data) => {
  if (!mcChartRef.value) return

  if (mcChart) {
    mcChart.dispose()
  }

  mcChart = echarts.init(mcChartRef.value)

  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(0, 0, 0, 0.05)',
      borderWidth: 1,
      textStyle: { color: '#1d1d1f' },
      padding: [12, 16]
    },
    legend: {
      data: ['中位数', '95%置信区间上限', '95%置信区间下限'],
      bottom: 0,
      itemGap: 24,
      textStyle: { color: '#86868b', fontSize: 13 }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      top: '5%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: data.dates,
      axisLine: { lineStyle: { color: 'rgba(0,0,0,0.1)' } },
      axisLabel: { color: '#86868b', fontSize: 12 }
    },
    yAxis: {
      type: 'value',
      name: '净值',
      nameTextStyle: { color: '#86868b' },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#86868b', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(0,0,0,0.05)' } }
    },
    series: [{
      name: '中位数',
      type: 'line',
      data: data.median,
      smooth: true,
      symbol: 'none',
      lineStyle: { width: 3, color: '#0071e3' },
      itemStyle: { color: '#0071e3' }
    }, {
      name: '95%置信区间上限',
      type: 'line',
      data: data.upper_95,
      smooth: true,
      symbol: 'none',
      lineStyle: { type: 'dashed', color: '#34c759' },
      itemStyle: { color: '#34c759' }
    }, {
      name: '95%置信区间下限',
      type: 'line',
      data: data.lower_95,
      smooth: true,
      symbol: 'none',
      lineStyle: { type: 'dashed', color: '#ff3b30' },
      itemStyle: { color: '#ff3b30' }
    }]
  }

  mcChart.setOption(option)
}

const initCorrelationChart = (data) => {
  if (!correlationChartRef.value) return

  if (correlationChart) {
    correlationChart.dispose()
  }

  correlationChart = echarts.init(correlationChartRef.value)

  const option = {
    tooltip: {
      position: 'top',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: 'rgba(0, 0, 0, 0.05)',
      borderWidth: 1,
      textStyle: { color: '#1d1d1f' },
      padding: [12, 16],
      formatter: function(params) {
        return `${params.name}<br/>相关性: ${params.value[2].toFixed(3)}`
      }
    },
    grid: {
      height: '70%',
      top: '10%',
      left: '15%'
    },
    xAxis: {
      type: 'category',
      data: data.products,
      splitArea: { show: true },
      axisLabel: { color: '#86868b', fontSize: 12, rotate: 30 }
    },
    yAxis: {
      type: 'category',
      data: data.products,
      splitArea: { show: true },
      axisLabel: { color: '#86868b', fontSize: 12 }
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: '5%',
      inRange: {
        color: ['#ff3b30', '#ff9500', '#ffffff', '#34c759', '#0071e3']
      },
      textStyle: { color: '#86868b' }
    },
    series: [{
      name: '相关性',
      type: 'heatmap',
      data: data.correlations,
      label: {
        show: true,
        formatter: function(params) {
          return params.value[2].toFixed(2)
        },
        fontSize: 11,
        color: '#1d1d1f'
      },
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowColor: 'rgba(0, 0, 0, 0.3)'
        }
      }
    }]
  }

  correlationChart.setOption(option)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.analysis-page {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 15px;
  color: #86868b;
  margin: 0;
}

.apple-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.apple-tabs :deep(.el-tabs__header) {
  margin-bottom: 24px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.apple-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.apple-tabs :deep(.el-tabs__item) {
  padding: 16px 24px;
  font-size: 15px;
  font-weight: 500;
  color: #86868b;
}

.apple-tabs :deep(.el-tabs__item.is-active) {
  color: #0071e3;
}

.apple-tabs :deep(.el-tabs__active-bar) {
  height: 3px;
  border-radius: 3px;
  background: linear-gradient(90deg, #0071e3 0%, #42a5f5 100%);
}

.tab-label {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tab-content {
  padding: 8px;
}

.control-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 14px;
  margin-bottom: 24px;
}

.control-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  min-width: 200px;
}

.control-label {
  font-size: 13px;
  font-weight: 500;
  color: #1d1d1f;
}

.apple-select {
  width: 100%;
}

.apple-select :deep(.el-input__wrapper) {
  background: white;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  padding: 4px 12px;
}

.apple-input-number {
  width: 100%;
}

.apple-input-number :deep(.el-input__wrapper) {
  background: white;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.apple-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
  border-radius: 12px;
  border: none;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  align-self: flex-start;
}

.apple-btn.primary {
  background: linear-gradient(135deg, #0071e3 0%, #42a5f5 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(0, 113, 227, 0.3);
}

.apple-btn.primary:hover:not(:disabled) {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 113, 227, 0.4);
}

.apple-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.result-panel {
  background: rgba(255, 255, 255, 0.6);
  border-radius: 14px;
  padding: 20px;
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.chart-container {
  height: 400px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 40px;
  text-align: center;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 14px;
  border: 2px dashed rgba(0, 0, 0, 0.06);
}

.empty-icon {
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 14px;
  color: #86868b;
  margin: 0;
}
</style>
