<template>
  <div class="backtest-page">
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">回测中心</h1>
        <p class="page-subtitle">管理和查看您的投资组合回测方案</p>
      </div>
      <button class="apple-btn primary" @click="createBacktest">
        <el-icon size="18"><Plus /></el-icon>
        <span>新建回测</span>
      </button>
    </div>

    <el-card class="apple-card" v-loading="loading">
      <div v-if="backtestList.length === 0" class="empty-state">
        <div class="empty-icon">
          <el-icon size="64" color="#c7c7cc"><DataAnalysis /></el-icon>
        </div>
        <h3>暂无回测方案</h3>
        <p>创建您的第一个回测方案来开始分析投资组合表现</p>
        <button class="apple-btn primary" @click="createBacktest">
          <el-icon><Plus /></el-icon>
          <span>立即创建</span>
        </button>
      </div>

      <div v-else class="backtest-list">
        <div
          v-for="item in backtestList"
          :key="item.id"
          class="backtest-item"
          @click="viewResult(item.id)"
        >
          <div class="item-main">
            <div class="item-icon" :class="getStrategyIcon(item.rebalance_strategy)">
              <el-icon size="24"><TrendCharts /></el-icon>
            </div>
            <div class="item-info">
              <div class="item-name">{{ item.name }}</div>
              <div class="item-meta">
                <span class="meta-item">
                  <el-icon><Calendar /></el-icon>
                  {{ item.start_date }} ~ {{ item.end_date }}
                </span>
                <span class="meta-item">
                  <el-icon><Money /></el-icon>
                  ¥{{ item.initial_amount?.toLocaleString() }}
                </span>
              </div>
            </div>
          </div>
          <div class="item-strategy">
            <span class="strategy-tag" :class="item.rebalance_strategy">
              {{ getStrategyLabel(item.rebalance_strategy) }}
            </span>
          </div>
          <div class="item-actions" @click.stop>
            <button class="action-btn view" @click="viewResult(item.id)">
              <el-icon><View /></el-icon>
            </button>
            <button class="action-btn delete" @click="deleteBacktest(item.id)">
              <el-icon><Delete /></el-icon>
            </button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useBacktestStore } from '@/stores/backtest'

const router = useRouter()
const backtestStore = useBacktestStore()
const loading = ref(false)
const backtestList = ref([])

const fetchBacktestList = async () => {
  loading.value = true
  try {
    const result = await backtestStore.fetchBacktestList()
    backtestList.value = result || []
  } catch (error) {
    ElMessage.error('获取回测列表失败')
  } finally {
    loading.value = false
  }
}

const createBacktest = () => {
  router.push('/backtest/config')
}

const viewResult = (id) => {
  router.push(`/backtest/result/${id}`)
}

const deleteBacktest = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个回测方案吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await backtestStore.deleteBacktest(id)
    ElMessage.success('删除成功')
    fetchBacktestList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const getStrategyLabel = (strategy) => {
  const labels = {
    'none': '不调整',
    'periodic': '定期再平衡',
    'threshold': '阈值再平衡'
  }
  return labels[strategy] || strategy
}

const getStrategyIcon = (strategy) => {
  const icons = {
    'none': 'gray',
    'periodic': 'blue',
    'threshold': 'green'
  }
  return icons[strategy] || 'gray'
}

onMounted(() => {
  fetchBacktestList()
})
</script>

<style scoped>
.backtest-page {
  padding: 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.apple-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
  border: none;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.apple-btn.primary {
  background: linear-gradient(135deg, #0071e3 0%, #42a5f5 100%);
  color: white;
  box-shadow: 0 4px 16px rgba(0, 113, 227, 0.3);
}

.apple-btn.primary:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 113, 227, 0.4);
}

.apple-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(20px);
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 40px;
  text-align: center;
}

.empty-icon {
  margin-bottom: 24px;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 8px 0;
}

.empty-state p {
  font-size: 15px;
  color: #86868b;
  margin: 0 0 24px 0;
}

.backtest-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 8px;
}

.backtest-item {
  display: flex;
  align-items: center;
  padding: 20px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 16px;
  border: 1px solid rgba(0, 0, 0, 0.04);
  cursor: pointer;
  transition: all 0.2s ease;
}

.backtest-item:hover {
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.item-main {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.item-icon {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.item-icon.blue {
  background: linear-gradient(135deg, #0071e3 0%, #42a5f5 100%);
  box-shadow: 0 4px 16px rgba(0, 113, 227, 0.3);
}

.item-icon.green {
  background: linear-gradient(135deg, #34c759 0%, #30d158 100%);
  box-shadow: 0 4px 16px rgba(52, 199, 89, 0.3);
}

.item-icon.gray {
  background: linear-gradient(135deg, #8e8e93 0%, #aeaeb2 100%);
  box-shadow: 0 4px 16px rgba(142, 142, 147, 0.3);
}

.item-info {
  flex: 1;
}

.item-name {
  font-size: 17px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 6px;
}

.item-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #86868b;
}

.item-strategy {
  margin-right: 20px;
}

.strategy-tag {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
}

.strategy-tag.none {
  background: rgba(142, 142, 147, 0.1);
  color: #8e8e93;
}

.strategy-tag.periodic {
  background: rgba(0, 113, 227, 0.1);
  color: #0071e3;
}

.strategy-tag.threshold {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.item-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: transparent;
  color: #86868b;
}

.action-btn:hover {
  background: rgba(0, 0, 0, 0.04);
}

.action-btn.view:hover {
  color: #0071e3;
}

.action-btn.delete:hover {
  color: #ff3b30;
  background: rgba(255, 59, 48, 0.1);
}
</style>
