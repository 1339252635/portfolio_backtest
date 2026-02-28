<template>
  <div class="backtest-result">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>回测结果: {{ result?.name }}</span>
          <el-button @click="goBack">返回</el-button>
        </div>
      </template>
      
      <div v-if="result">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-statistic title="年化收益率" :value="metrics?.annual_return" suffix="%" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="年化波动率" :value="metrics?.annual_volatility" suffix="%" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="最大回撤" :value="metrics?.max_drawdown" suffix="%" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="夏普比率" :value="metrics?.sharpe_ratio" />
          </el-col>
        </el-row>
        
        <el-divider />
        
        <h3>净值曲线</h3>
        <div ref="chartRef" style="height: 400px;"></div>
        
        <el-divider />
        
        <h3>持仓明细</h3>
        <el-table :data="holdings" style="width: 100%">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="product_code" label="产品代码" width="120" />
          <el-table-column prop="shares" label="份额" />
          <el-table-column prop="value" label="市值" />
          <el-table-column prop="weight" label="权重" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { useBacktestStore } from '@/stores/backtest'

const route = useRoute()
const router = useRouter()
const backtestStore = useBacktestStore()

const loading = ref(false)
const result = ref(null)
const metrics = ref(null)
const holdings = ref([])
const chartRef = ref(null)
let chart = null

const fetchResult = async () => {
  const id = route.params.id
  if (!id) return
   
  loading.value = true
  try {
    const data = await backtestStore.fetchBacktestResult(id)
    result.value = data.scenario
    metrics.value = data.metrics
    holdings.value = data.holdings || []
    
    nextTick(() => {
      initChart(data.daily_values)
    })
  } catch (error) {
    ElMessage.error('获取回测结果失败')
  } finally {
    loading.value = false
  }
}

const initChart = (dailyValues) => {
  if (!chartRef.value || !dailyValues) return
   
  chart = echarts.init(chartRef.value)
  
  const dates = dailyValues.map(item => item.date)
  const values = dailyValues.map(item => item.portfolio_value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value',
      name: '净值'
    },
    series: [{
      name: '组合净值',
      type: 'line',
      data: values,
      smooth: true,
      areaStyle: {
        opacity: 0.3
      }
    }]
  }
  
  chart.setOption(option)
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchResult()
})
</script>

<style scoped>
.backtest-result {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
