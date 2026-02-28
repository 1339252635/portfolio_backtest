<template>
  <div class="realtime-market">
    <el-card class="market-header">
      <template #header>
        <div class="header-content">
          <span class="title">实时行情</span>
          <el-tag :type="isMarketOpen ? 'success' : 'info'" effect="dark">
            {{ isMarketOpen ? '交易中' : '已收盘' }}
          </el-tag>
          <el-button type="primary" size="small" @click="refreshData" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <!-- 市场概览 -->
      <div class="market-overview">
        <h3>市场概览</h3>
        <el-row :gutter="20">
          <el-col :span="4" v-for="(index, code) in marketOverview" :key="code">
            <div class="index-card" :class="getChangeClass(index.change)">
              <div class="index-name">{{ index.name }}</div>
              <div class="index-price">{{ formatNumber(index.price) }}</div>
              <div class="index-change">
                <span :class="getChangeClass(index.change)">
                  {{ index.change >= 0 ? '+' : '' }}{{ formatNumber(index.change) }}%
                </span>
              </div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 产品实时行情 -->
    <el-card class="products-realtime">
      <template #header>
        <div class="header-content">
          <span class="title">产品实时行情</span>
          <div class="header-actions">
            <el-switch
              v-model="autoRefresh"
              active-text="自动刷新"
              :active-value="true"
              :inactive-value="false"
            />
            <el-select v-model="refreshInterval" size="small" style="width: 120px; margin-left: 10px;">
              <el-option label="5秒" :value="5" />
              <el-option label="10秒" :value="10" />
              <el-option label="30秒" :value="30" />
              <el-option label="1分钟" :value="60" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table
        :data="productsRealtime"
        v-loading="loading"
        style="width: 100%"
        :default-sort="{ prop: 'change', order: 'descending' }"
      >
        <el-table-column prop="code" label="代码" width="100" sortable />
        <el-table-column prop="name" label="名称" width="150" />
        <el-table-column prop="price" label="最新价" width="120" sortable>
          <template #default="{ row }">
            <span :class="getChangeClass(row.change)">
              {{ formatNumber(row.price, 3) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="change" label="涨跌幅" width="120" sortable>
          <template #default="{ row }">
            <span :class="getChangeClass(row.change)">
              {{ row.change >= 0 ? '+' : '' }}{{ formatNumber(row.change) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="change_amount" label="涨跌额" width="120">
          <template #default="{ row }">
            <span :class="getChangeClass(row.change_amount)">
              {{ row.change_amount >= 0 ? '+' : '' }}{{ formatNumber(row.change_amount) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="volume" label="成交量" width="150">
          <template #default="{ row }">
            {{ formatVolume(row.volume) }}
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="成交额" width="150">
          <template #default="{ row }">
            {{ formatAmount(row.amount) }}
          </template>
        </el-table-column>
        <el-table-column prop="open" label="开盘价" width="100">
          <template #default="{ row }">
            {{ formatNumber(row.open, 3) }}
          </template>
        </el-table-column>
        <el-table-column prop="high" label="最高价" width="100">
          <template #default="{ row }">
            {{ formatNumber(row.high, 3) }}
          </template>
        </el-table-column>
        <el-table-column prop="low" label="最低价" width="100">
          <template #default="{ row }">
            {{ formatNumber(row.low, 3) }}
          </template>
        </el-table-column>
        <el-table-column prop="timestamp" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getMarketOverview, getAllProductsRealtime } from '@/api/realtime'

const loading = ref(false)
const autoRefresh = ref(true)
const refreshInterval = ref(10)
const marketOverview = ref({})
const productsRealtime = ref([])
const isMarketOpen = ref(false)
let refreshTimer = null

// 检查是否交易时间
const checkMarketOpen = () => {
  const now = new Date()
  const hour = now.getHours()
  const minute = now.getMinutes()
  const day = now.getDay()
  
  // 周一到周五
  if (day >= 1 && day <= 5) {
    // 上午 9:30-11:30 或 下午 13:00-15:00
    if ((hour === 9 && minute >= 30) || (hour === 10) || (hour === 11 && minute <= 30) ||
        (hour === 13) || (hour === 14)) {
      isMarketOpen.value = true
      return
    }
  }
  isMarketOpen.value = false
}

// 获取市场概览
const fetchMarketOverview = async () => {
  try {
    const res = await getMarketOverview()
    if (res.data.code === 200) {
      marketOverview.value = res.data.data
    }
  } catch (error) {
    console.error('Failed to fetch market overview:', error)
  }
}

// 获取产品实时行情
const fetchProductsRealtime = async () => {
  loading.value = true
  try {
    const res = await getAllProductsRealtime()
    if (res.data.code === 200) {
      productsRealtime.value = Object.values(res.data.data)
      // 显示后台更新提示
      if (res.data.message && res.data.message.includes('updating')) {
        console.log(res.data.message)
      }
    }
  } catch (error) {
    console.error('Failed to fetch products realtime:', error)
    // 如果是超时错误，显示更友好的提示
    if (error.code === 'ECONNABORTED') {
      ElMessage.warning('数据获取超时，请稍后重试')
    } else {
      ElMessage.error('获取实时行情失败')
    }
  } finally {
    loading.value = false
  }
}

// 刷新所有数据
const refreshData = async () => {
  checkMarketOpen()
  await Promise.all([
    fetchMarketOverview(),
    fetchProductsRealtime()
  ])
  ElMessage.success('数据已更新')
}

// 自动刷新
const startAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  if (autoRefresh.value) {
    refreshTimer = setInterval(() => {
      fetchMarketOverview()
      fetchProductsRealtime()
    }, refreshInterval.value * 1000)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 监听自动刷新设置
watch(autoRefresh, (newVal) => {
  if (newVal) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
})

// 监听刷新间隔
watch(refreshInterval, () => {
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

// 格式化数字
const formatNumber = (num, decimals = 2) => {
  if (num === null || num === undefined) return '-'
  return Number(num).toFixed(decimals)
}

// 格式化成交量
const formatVolume = (volume) => {
  if (!volume) return '-'
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

// 格式化成交额
const formatAmount = (amount) => {
  if (!amount) return '-'
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toFixed(2)
}

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp)
  return date.toLocaleString('zh-CN')
}

// 获取涨跌样式类
const getChangeClass = (change) => {
  if (change > 0) return 'rise'
  if (change < 0) return 'fall'
  return 'neutral'
}

onMounted(() => {
  refreshData()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.realtime-market {
  padding: 20px;
}

.market-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.market-overview {
  margin-top: 20px;
}

.market-overview h3 {
  margin-bottom: 15px;
  color: #303133;
}

.index-card {
  text-align: center;
  padding: 15px;
  border-radius: 8px;
  background: #f5f7fa;
  transition: all 0.3s;
}

.index-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.index-name {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

.index-price {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 5px;
}

.index-change {
  font-size: 14px;
}

.products-realtime {
  margin-top: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  margin-left: auto;
}

.rise {
  color: #f56c6c;
}

.fall {
  color: #67c23a;
}

.neutral {
  color: #909399;
}
</style>
