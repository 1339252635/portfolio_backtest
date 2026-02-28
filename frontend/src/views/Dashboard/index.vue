<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="24" class="stats-row">
      <el-col :span="6">
        <div class="apple-stat-card">
          <div class="stat-icon blue">
            <el-icon size="28"><Collection /></el-icon>
          </div>
          <div class="stat-content">
            <div class="apple-stat-value">{{ products.length }}</div>
            <div class="apple-stat-label">产品数量</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="apple-stat-card">
          <div class="stat-icon green">
            <el-icon size="28"><DataAnalysis /></el-icon>
          </div>
          <div class="stat-content">
            <div class="apple-stat-value">{{ scenarios.length }}</div>
            <div class="apple-stat-label">回测方案</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="apple-stat-card">
          <div class="stat-icon orange">
            <el-icon size="28"><TrendCharts /></el-icon>
          </div>
          <div class="stat-content">
            <div class="apple-stat-value">{{ etfCount }}</div>
            <div class="apple-stat-label">ETF产品</div>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="apple-stat-card">
          <div class="stat-icon purple">
            <el-icon size="28"><Money /></el-icon>
          </div>
          <div class="stat-content">
            <div class="apple-stat-value">{{ fundCount }}</div>
            <div class="apple-stat-label">基金产品</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-row :gutter="24" class="action-row">
      <el-col :span="12">
        <el-card class="apple-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <button class="apple-action-btn primary" @click="$router.push('/backtest/config')">
              <div class="btn-icon">
                <el-icon size="20"><Plus /></el-icon>
              </div>
              <div class="btn-text">
                <div class="btn-title">新建回测</div>
                <div class="btn-desc">创建新的回测方案</div>
              </div>
            </button>
            <button class="apple-action-btn secondary" @click="$router.push('/products')">
              <div class="btn-icon">
                <el-icon size="20"><Collection /></el-icon>
              </div>
              <div class="btn-text">
                <div class="btn-title">管理产品</div>
                <div class="btn-desc">查看和编辑产品</div>
              </div>
            </button>
            <button class="apple-action-btn secondary" @click="initDefaults">
              <div class="btn-icon">
                <el-icon size="20"><Download /></el-icon>
              </div>
              <div class="btn-text">
                <div class="btn-title">初始化产品</div>
                <div class="btn-desc">加载默认产品数据</div>
              </div>
            </button>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="apple-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">最近回测</span>
              <el-button text type="primary" @click="$router.push('/backtest')">查看全部</el-button>
            </div>
          </template>
          <div class="recent-list">
            <div v-for="scenario in recentScenarios" :key="scenario.id" class="recent-item" @click="viewResult(scenario.id)">
              <div class="recent-info">
                <div class="recent-name">{{ scenario.name }}</div>
                <div class="recent-date">{{ scenario.start_date }} ~ {{ scenario.end_date }}</div>
              </div>
              <el-icon class="recent-arrow"><ArrowRight /></el-icon>
            </div>
            <div v-if="recentScenarios.length === 0" class="empty-state">
              <el-icon size="48" color="#c0c4cc"><Document /></el-icon>
              <p>暂无回测记录</p>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 产品分布 -->
    <el-row :gutter="24" class="chart-row">
      <el-col :span="12">
        <el-card class="apple-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">产品类型分布</span>
            </div>
          </template>
          <v-chart class="chart" :option="productTypeChartOption" autoresize />
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="apple-card">
          <template #header>
            <div class="card-header">
              <span class="card-title">资产配置示例</span>
            </div>
          </template>
          <v-chart class="chart" :option="allocationExampleOption" autoresize />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProductsStore } from '@/stores/products'
import { useBacktestStore } from '@/stores/backtest'
import { ElMessage } from 'element-plus'

const router = useRouter()
const productsStore = useProductsStore()
const backtestStore = useBacktestStore()

const products = computed(() => productsStore.products)
const scenarios = computed(() => backtestStore.scenarios)
const etfCount = computed(() => products.value.filter(p => p.type === 'ETF').length)
const fundCount = computed(() => products.value.filter(p => p.type !== 'ETF').length)
const recentScenarios = computed(() => scenarios.value.slice(0, 5))

// 产品类型分布图表 - Apple风格配色
const productTypeChartOption = computed(() => {
  const etfCount = products.value.filter(p => p.type === 'ETF').length
  const fundCount = products.value.filter(p => p.type !== 'ETF').length
  
  return {
    tooltip: { 
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: 'rgba(0, 0, 0, 0.05)',
      borderWidth: 1,
      textStyle: { color: '#1d1d1f' }
    },
    legend: { 
      bottom: '5%',
      textStyle: { color: '#86868b' }
    },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 12,
        borderColor: '#fff',
        borderWidth: 3
      },
      label: { show: false },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 600
        }
      },
      data: [
        { value: etfCount, name: 'ETF', itemStyle: { color: '#0071e3' } },
        { value: fundCount, name: '基金', itemStyle: { color: '#34c759' } }
      ]
    }]
  }
})

// 资产配置示例图表 - Apple风格配色
const allocationExampleOption = computed(() => {
  return {
    tooltip: { 
      trigger: 'item',
      backgroundColor: 'rgba(255, 255, 255, 0.9)',
      borderColor: 'rgba(0, 0, 0, 0.05)',
      borderWidth: 1,
      textStyle: { color: '#1d1d1f' }
    },
    legend: { 
      bottom: '5%',
      textStyle: { color: '#86868b' }
    },
    series: [{
      type: 'pie',
      radius: '65%',
      center: ['50%', '45%'],
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 2
      },
      data: [
        { value: 40, name: '纳指ETF', itemStyle: { color: '#0071e3' } },
        { value: 20, name: '标普ETF', itemStyle: { color: '#5ac8fa' } },
        { value: 20, name: '混债基金', itemStyle: { color: '#34c759' } },
        { value: 10, name: '红利低波', itemStyle: { color: '#ff9500' } },
        { value: 10, name: '中证A50', itemStyle: { color: '#af52de' } }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 20,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.2)'
        }
      }
    }]
  }
})

const initDefaults = async () => {
  try {
    await productsStore.initDefaultProducts()
    await productsStore.fetchProducts()
    ElMessage.success('默认产品初始化成功')
  } catch (error) {
    ElMessage.error('初始化失败')
  }
}

const viewResult = (id) => {
  router.push(`/backtest/result/${id}`)
}

onMounted(() => {
  productsStore.fetchProducts()
  backtestStore.fetchScenarios()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stats-row {
  margin-bottom: 24px;
}

.apple-stat-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 18px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.apple-stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon.blue {
  background: linear-gradient(135deg, #0071e3 0%, #42a5f5 100%);
  box-shadow: 0 4px 16px rgba(0, 113, 227, 0.3);
}

.stat-icon.green {
  background: linear-gradient(135deg, #34c759 0%, #30d158 100%);
  box-shadow: 0 4px 16px rgba(52, 199, 89, 0.3);
}

.stat-icon.orange {
  background: linear-gradient(135deg, #ff9500 0%, #ffcc00 100%);
  box-shadow: 0 4px 16px rgba(255, 149, 0, 0.3);
}

.stat-icon.purple {
  background: linear-gradient(135deg, #af52de 0%, #bf5af2 100%);
  box-shadow: 0 4px 16px rgba(175, 82, 222, 0.3);
}

.stat-content {
  flex: 1;
}

.apple-stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #1d1d1f;
  letter-spacing: -0.5px;
  line-height: 1.2;
}

.apple-stat-label {
  font-size: 13px;
  color: #86868b;
  margin-top: 4px;
}

.action-row {
  margin-bottom: 24px;
}

.apple-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 17px;
  font-weight: 600;
  color: #1d1d1f;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.apple-action-btn {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  border-radius: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  width: 100%;
}

.apple-action-btn.primary {
  background: linear-gradient(135deg, #0071e3 0%, #42a5f5 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(0, 113, 227, 0.3);
}

.apple-action-btn.primary:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 113, 227, 0.4);
}

.apple-action-btn.secondary {
  background: rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
}

.apple-action-btn.secondary:hover {
  background: rgba(0, 0, 0, 0.08);
}

.btn-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.apple-action-btn.secondary .btn-icon {
  background: rgba(0, 0, 0, 0.06);
}

.btn-text {
  flex: 1;
}

.btn-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 2px;
}

.btn-desc {
  font-size: 13px;
  opacity: 0.7;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recent-item {
  display: flex;
  align-items: center;
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.recent-item:hover {
  background: rgba(0, 0, 0, 0.04);
}

.recent-info {
  flex: 1;
}

.recent-name {
  font-size: 15px;
  font-weight: 500;
  color: #1d1d1f;
  margin-bottom: 4px;
}

.recent-date {
  font-size: 13px;
  color: #86868b;
}

.recent-arrow {
  color: #c7c7cc;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #c0c4cc;
}

.empty-state p {
  margin-top: 12px;
  font-size: 14px;
}

.chart-row {
  margin-bottom: 24px;
}

.chart {
  height: 320px;
}
</style>
