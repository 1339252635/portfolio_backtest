<template>
  <div class="smart-allocation-page">
    <div class="page-header">
      <h1 class="page-title">智能配置建议</h1>
      <p class="page-subtitle">基于您的风险承受能力，为您推荐最优资产配置方案</p>
    </div>

    <div class="content-grid">
      <!-- 风险评估问卷 -->
      <div class="card risk-assessment-card" v-if="!showResult">
        <div class="card-header">
          <div class="header-icon">
            <el-icon><QuestionFilled /></el-icon>
          </div>
          <div class="header-content">
            <h2 class="card-title">风险承受能力评估</h2>
            <p class="card-subtitle">请回答以下问题，帮助我们了解您的投资偏好</p>
          </div>
        </div>

        <div class="assessment-form">
          <!-- 年龄 -->
          <div class="form-section">
            <label class="section-label">您的年龄</label>
            <div class="age-slider">
              <el-slider
                v-model="assessment.age"
                :min="18"
                :max="80"
                :step="1"
                show-stops
              />
              <span class="age-value">{{ assessment.age }} 岁</span>
            </div>
          </div>

          <!-- 投资经验 -->
          <div class="form-section">
            <label class="section-label">投资经验（年）</label>
            <div class="experience-options">
              <button
                v-for="opt in experienceOptions"
                :key="opt.value"
                class="option-btn"
                :class="{ active: assessment.investment_experience === opt.value }"
                @click="assessment.investment_experience = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- 年收入 -->
          <div class="form-section">
            <label class="section-label">年收入范围</label>
            <div class="income-options">
              <button
                v-for="opt in incomeOptions"
                :key="opt.value"
                class="option-btn"
                :class="{ active: assessment.annual_income === opt.value }"
                @click="assessment.annual_income = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- 流动资产 -->
          <div class="form-section">
            <label class="section-label">流动资产规模</label>
            <div class="assets-options">
              <button
                v-for="opt in assetsOptions"
                :key="opt.value"
                class="option-btn"
                :class="{ active: assessment.liquid_assets === opt.value }"
                @click="assessment.liquid_assets = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- 投资期限 -->
          <div class="form-section">
            <label class="section-label">投资期限</label>
            <div class="horizon-options">
              <button
                v-for="opt in horizonOptions"
                :key="opt.value"
                class="option-btn"
                :class="{ active: assessment.investment_horizon === opt.value }"
                @click="assessment.investment_horizon = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- 最大可承受损失 -->
          <div class="form-section">
            <label class="section-label">最大可承受损失</label>
            <div class="loss-options">
              <button
                v-for="opt in lossOptions"
                :key="opt.value"
                class="option-btn"
                :class="{ active: assessment.loss_tolerance === opt.value }"
                @click="assessment.loss_tolerance = opt.value"
              >
                {{ opt.label }}
              </button>
            </div>
          </div>

          <!-- 每月投资金额 -->
          <div class="form-section">
            <label class="section-label">每月计划投资金额</label>
            <el-input-number
              v-model="assessment.monthly_investment"
              :min="1000"
              :max="1000000"
              :step="1000"
              class="investment-input"
            />
            <span class="input-unit">元</span>
          </div>

          <!-- 投资目标 -->
          <div class="form-section">
            <label class="section-label">主要投资目标</label>
            <div class="goal-options">
              <button
                v-for="opt in goalOptions"
                :key="opt.value"
                class="option-btn goal-btn"
                :class="{ active: assessment.investment_goal === opt.value }"
                @click="assessment.investment_goal = opt.value"
              >
                <el-icon class="goal-icon"><component :is="opt.icon" /></el-icon>
                <span class="goal-text">{{ opt.label }}</span>
              </button>
            </div>
          </div>

          <!-- 提交按钮 -->
          <div class="form-actions">
            <button class="apple-btn apple-btn-primary btn-large" @click="submitAssessment" :disabled="loading">
              <el-icon v-if="loading" class="is-loading"><Loading /></el-icon>
              <span>{{ loading ? '分析中...' : '获取智能配置建议' }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 评估结果 -->
      <div class="result-container" v-else>
        <!-- 风险等级卡片 -->
        <div class="card risk-level-card">
          <div class="risk-badge" :class="result.risk_level">
            {{ riskLevelText }}
          </div>
          <h2 class="result-title">您的风险承受能力评估结果</h2>
          <p class="result-desc">{{ riskLevelDescription }}</p>
          
          <div class="risk-metrics">
            <div class="metric-item">
              <span class="metric-label">风险评分</span>
              <div class="metric-value">
                <el-progress
                  :percentage="result.risk_score"
                  :color="riskProgressColor"
                  :stroke-width="12"
                  :show-text="false"
                />
                <span class="score-text">{{ result.risk_score }}/100</span>
              </div>
            </div>
            <div class="metric-item">
              <span class="metric-label">建议权益仓位</span>
              <span class="metric-value-text">{{ result.suggested_equity_ratio }}%</span>
            </div>
          </div>

          <div class="goal-match">
            <el-icon><CircleCheck /></el-icon>
            <span>匹配投资目标：<strong>{{ goalText }}</strong></span>
          </div>
        </div>

        <!-- 资产配置建议 -->
        <div class="card allocation-card">
          <div class="card-header">
            <div class="header-icon allocation-icon">
              <el-icon><PieChart /></el-icon>
            </div>
            <div class="header-content">
              <h2 class="card-title">推荐资产配置方案</h2>
              <p class="card-subtitle">基于您的风险等级，我们为您推荐以下配置</p>
            </div>
          </div>

          <div class="allocation-chart">
            <div class="chart-container">
              <div ref="pieChart" class="pie-chart"></div>
            </div>
            <div class="allocation-legend">
              <div
                v-for="(item, index) in allocationItems"
                :key="index"
                class="legend-item"
              >
                <span class="legend-color" :style="{ background: item.color }"></span>
                <span class="legend-name">{{ item.name }}</span>
                <span class="legend-value">{{ item.value }}%</span>
              </div>
            </div>
          </div>

          <!-- 配置说明 -->
          <div class="allocation-notes">
            <h3 class="notes-title">配置逻辑</h3>
            <ul class="notes-list">
              <li v-for="(note, index) in allocationNotes" :key="index">
                <el-icon><InfoFilled /></el-icon>
                <span>{{ note }}</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- 市场调整建议 -->
        <div class="card market-adjust-card">
          <div class="card-header">
            <div class="header-icon market-icon">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="header-content">
              <h2 class="card-title">市场环境调整建议</h2>
              <p class="card-subtitle">根据当前市场环境，可考虑以下调整</p>
            </div>
          </div>

          <div class="market-options">
            <div
              v-for="market in marketConditions"
              :key="market.value"
              class="market-option"
              :class="{ active: selectedMarket === market.value }"
              @click="selectMarket(market.value)"
            >
              <el-icon class="market-icon-large"><component :is="market.icon" /></el-icon>
              <span class="market-name">{{ market.label }}</span>
              <span class="market-desc">{{ market.desc }}</span>
            </div>
          </div>

          <div v-if="marketAdjustment" class="adjustment-result">
            <h4>调整后配置</h4>
            <div class="adjustment-comparison">
              <div class="comparison-item" v-for="(adj, name) in marketAdjustment.adjustments" :key="name">
                <span class="asset-name">{{ name }}</span>
                <div class="adjustment-bar">
                  <div class="original-bar" :style="{ width: adj.original + '%' }"></div>
                  <div class="adjusted-bar" :style="{ width: adj.adjusted + '%', left: 0 }"></div>
                </div>
                <div class="adjustment-values">
                  <span class="original">{{ adj.original }}%</span>
                  <el-icon><ArrowRight /></el-icon>
                  <span class="adjusted" :class="{ up: adj.adjusted > adj.original, down: adj.adjusted < adj.original }">
                    {{ adj.adjusted }}%
                  </span>
                </div>
              </div>
            </div>
            <div class="adjustment-reason">
              <el-icon><InfoFilled /></el-icon>
              <span>{{ marketAdjustment.reason }}</span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="result-actions">
          <button class="apple-btn apple-btn-secondary" @click="resetAssessment">
            <el-icon><RefreshLeft /></el-icon>
            <span>重新评估</span>
          </button>
          <button class="apple-btn apple-btn-primary" @click="applyToBacktest">
            <el-icon><ArrowRight /></el-icon>
            <span>应用到回测</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import {
  QuestionFilled,
  PieChart,
  TrendCharts,
  CircleCheck,
  InfoFilled,
  Loading,
  RefreshLeft,
  ArrowRight,
  Wallet,
  Money,
  TrendArrowUp,
  Trophy
} from '@element-plus/icons-vue'
import { assessRisk, adjustByMarket, getAllocationTemplates } from '@/api/smartAllocation'

const router = useRouter()
const loading = ref(false)
const showResult = ref(false)
const result = ref(null)
const pieChart = ref(null)
const selectedMarket = ref(null)
const marketAdjustment = ref(null)

// 评估表单数据
const assessment = reactive({
  age: 30,
  investment_experience: 1,
  annual_income: 100000,
  liquid_assets: 100000,
  investment_horizon: 3,
  loss_tolerance: 10,
  monthly_investment: 5000,
  investment_goal: 'balanced_growth'
})

// 选项配置
const experienceOptions = [
  { label: '1年以下', value: 0.5 },
  { label: '1-3年', value: 2 },
  { label: '3-5年', value: 4 },
  { label: '5-10年', value: 7 },
  { label: '10年以上', value: 12 }
]

const incomeOptions = [
  { label: '10万以下', value: 80000 },
  { label: '10-20万', value: 150000 },
  { label: '20-50万', value: 350000 },
  { label: '50-100万', value: 750000 },
  { label: '100万以上', value: 150000 }
]

const assetsOptions = [
  { label: '10万以下', value: 80000 },
  { label: '10-50万', value: 300000 },
  { label: '50-100万', value: 750000 },
  { label: '100-500万', value: 3000000 },
  { label: '500万以上', value: 8000000 }
]

const horizonOptions = [
  { label: '1年以内', value: 0.5 },
  { label: '1-3年', value: 2 },
  { label: '3-5年', value: 4 },
  { label: '5-10年', value: 7 },
  { label: '10年以上', value: 15 }
]

const lossOptions = [
  { label: '5%以内', value: 5 },
  { label: '5-10%', value: 10 },
  { label: '10-20%', value: 20 },
  { label: '20-30%', value: 30 },
  { label: '30%以上', value: 40 }
]

const goalOptions = [
  { label: '资产保值', value: 'capital_preservation', icon: 'Wallet' },
  { label: '稳定收益', value: 'steady_income', icon: 'Money' },
  { label: '平衡增长', value: 'balanced_growth', icon: 'TrendArrowUp' },
  { label: '资本增值', value: 'capital_growth', icon: 'Trophy' },
  { label: '激进增长', value: 'aggressive_growth', icon: 'TrendCharts' }
]

const marketConditions = [
  { label: '牛市', value: 'bull', icon: 'TrendArrowUp', desc: '市场上涨，可适当增加权益仓位' },
  { label: '熊市', value: 'bear', icon: 'TrendCharts', desc: '市场下跌，建议降低风险敞口' },
  { label: '震荡市', value: 'sideways', icon: 'RefreshLeft', desc: '市场震荡，保持均衡配置' }
]

// 配置颜色
const allocationColors = {
  '混债基金': '#34C759',
  '红利低波': '#5856D6',
  '中证A50': '#007AFF',
  '标普ETF': '#FF9500',
  '纳指ETF': '#FF3B30'
}

// 计算属性
const riskLevelText = computed(() => {
  const levels = {
    conservative: '保守型',
    cautious: '谨慎型',
    balanced: '平衡型',
    aggressive: '进取型',
    radical: '激进型'
  }
  return levels[result.value?.risk_level] || '未知'
})

const riskLevelDescription = computed(() => {
  const descriptions = {
    conservative: '您偏好稳健投资，注重本金安全，适合低风险资产配置。',
    cautious: '您倾向于保守投资，可接受小幅波动以获取稳定收益。',
    balanced: '您追求风险与收益的平衡，愿意承担适度风险。',
    aggressive: '您追求较高收益，可接受较大波动和短期亏损。',
    radical: '您追求最大化收益，愿意承担高风险和大幅波动。'
  }
  return descriptions[result.value?.risk_level] || ''
})

const riskProgressColor = computed(() => {
  const colors = {
    conservative: '#34C759',
    cautious: '#5856D6',
    balanced: '#007AFF',
    aggressive: '#FF9500',
    radical: '#FF3B30'
  }
  return colors[result.value?.risk_level] || '#007AFF'
})

const goalText = computed(() => {
  const goal = goalOptions.find(g => g.value === assessment.investment_goal)
  return goal?.label || '平衡增长'
})

const allocationItems = computed(() => {
  if (!result.value?.allocation) return []
  return Object.entries(result.value.allocation).map(([name, value]) => ({
    name,
    value,
    color: allocationColors[name] || '#999'
  }))
})

const allocationNotes = computed(() => {
  const notes = {
    conservative: [
      '以债券基金为主，确保本金安全',
      '少量配置红利低波股票，获取稳定分红',
      '权益仓位控制在20%以内'
    ],
    cautious: [
      '债券基金占比40%，提供稳定收益基础',
      '红利低波策略降低权益波动',
      '权益仓位控制在35%以内'
    ],
    balanced: [
      '股债均衡配置，分散风险',
      'A股与美股均衡配置，分散地域风险',
      '权益仓位控制在55%以内'
    ],
    aggressive: [
      '以权益资产为主，追求资本增值',
      '增加美股配置比例，分享全球增长',
      '权益仓位可达75%'
    ],
    radical: [
      '全权益配置，追求最大化收益',
      '重点配置美股ETF，把握全球机会',
      '权益仓位可达100%'
    ]
  }
  return notes[result.value?.risk_level] || []
})

// 提交评估
const submitAssessment = async () => {
  loading.value = true
  try {
    const res = await assessRisk({
      age: assessment.age,
      investment_experience: assessment.investment_experience,
      annual_income: assessment.annual_income,
      liquid_assets: assessment.liquid_assets,
      investment_horizon: assessment.investment_horizon,
      loss_tolerance: assessment.loss_tolerance,
      monthly_investment: assessment.monthly_investment,
      investment_goal: assessment.investment_goal
    })
    
    if (res.code === 200) {
      result.value = res.data
      showResult.value = true
      nextTick(() => {
        initPieChart()
      })
    }
  } catch (error) {
    ElMessage.error('评估失败，请重试')
  } finally {
    loading.value = false
  }
}

// 初始化饼图
const initPieChart = () => {
  if (!pieChart.value || !result.value?.allocation) return
  
  const chart = echarts.init(pieChart.value)
  const data = Object.entries(result.value.allocation).map(([name, value]) => ({
    name,
    value,
    itemStyle: { color: allocationColors[name] }
  }))
  
  chart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}%'
    },
    series: [{
      type: 'pie',
      radius: ['45%', '75%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2
      },
      label: {
        show: false
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      data
    }]
  })
}

// 选择市场环境
const selectMarket = async (market) => {
  selectedMarket.value = market
  try {
    const res = await adjustByMarket({
      risk_level: result.value.risk_level,
      market_condition: market
    })
    
    if (res.code === 200) {
      marketAdjustment.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取调整建议失败')
  }
}

// 重置评估
const resetAssessment = () => {
  showResult.value = false
  result.value = null
  selectedMarket.value = null
  marketAdjustment.value = null
}

// 应用到回测
const applyToBacktest = () => {
  // 将配置保存到 localStorage，在回测页面读取
  const config = {
    allocation: result.value.allocation,
    riskLevel: result.value.risk_level,
    riskScore: result.value.risk_score
  }
  localStorage.setItem('smartAllocationConfig', JSON.stringify(config))
  router.push('/backtest/config')
}

onMounted(() => {
  // 页面加载逻辑
})
</script>

<style scoped>
.smart-allocation-page {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
}

.page-title {
  font-size: 34px;
  font-weight: 700;
  color: var(--apple-text);
  margin-bottom: 8px;
  letter-spacing: -0.5px;
}

.page-subtitle {
  font-size: 17px;
  color: var(--apple-text-secondary);
}

.content-grid {
  display: grid;
  gap: 24px;
}

.card {
  background: var(--apple-card-bg);
  border-radius: 20px;
  padding: 28px;
  box-shadow: var(--apple-shadow);
  border: 1px solid var(--apple-border);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: linear-gradient(135deg, #007AFF, #5856D6);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.header-icon.allocation-icon {
  background: linear-gradient(135deg, #34C759, #30D158);
}

.header-icon.market-icon {
  background: linear-gradient(135deg, #FF9500, #FF6B35);
}

.card-title {
  font-size: 21px;
  font-weight: 600;
  color: var(--apple-text);
  margin-bottom: 4px;
}

.card-subtitle {
  font-size: 14px;
  color: var(--apple-text-secondary);
}

/* 评估表单样式 */
.assessment-form {
  display: grid;
  gap: 24px;
}

.form-section {
  padding-bottom: 20px;
  border-bottom: 1px solid var(--apple-border);
}

.form-section:last-of-type {
  border-bottom: none;
}

.section-label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: var(--apple-text);
  margin-bottom: 12px;
}

.age-slider {
  display: flex;
  align-items: center;
  gap: 16px;
}

.age-slider :deep(.el-slider) {
  flex: 1;
}

.age-value {
  font-size: 17px;
  font-weight: 600;
  color: var(--apple-primary);
  min-width: 60px;
  text-align: right;
}

.option-btn {
  padding: 10px 20px;
  border: 1.5px solid var(--apple-border);
  border-radius: 12px;
  background: var(--apple-bg);
  color: var(--apple-text);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.option-btn:hover {
  border-color: var(--apple-primary);
  color: var(--apple-primary);
}

.option-btn.active {
  background: var(--apple-primary);
  border-color: var(--apple-primary);
  color: white;
}

.experience-options,
.income-options,
.assets-options,
.horizon-options,
.loss-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.goal-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.option-btn.goal-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
}

.goal-icon {
  font-size: 24px;
}

.goal-text {
  font-size: 13px;
}

.investment-input {
  width: 160px;
}

.input-unit {
  margin-left: 8px;
  font-size: 15px;
  color: var(--apple-text-secondary);
}

.form-actions {
  display: flex;
  justify-content: center;
  padding-top: 8px;
}

.btn-large {
  padding: 14px 32px;
  font-size: 16px;
}

/* 结果页面样式 */
.result-container {
  display: grid;
  gap: 24px;
}

.risk-level-card {
  text-align: center;
  padding: 32px;
}

.risk-badge {
  display: inline-block;
  padding: 8px 24px;
  border-radius: 20px;
  font-size: 18px;
  font-weight: 700;
  color: white;
  margin-bottom: 20px;
}

.risk-badge.conservative {
  background: linear-gradient(135deg, #34C759, #30D158);
}

.risk-badge.cautious {
  background: linear-gradient(135deg, #5856D6, #AF52DE);
}

.risk-badge.balanced {
  background: linear-gradient(135deg, #007AFF, #5AC8FA);
}

.risk-badge.aggressive {
  background: linear-gradient(135deg, #FF9500, #FF6B35);
}

.risk-badge.radical {
  background: linear-gradient(135deg, #FF3B30, #FF6B6B);
}

.result-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--apple-text);
  margin-bottom: 8px;
}

.result-desc {
  font-size: 15px;
  color: var(--apple-text-secondary);
  margin-bottom: 24px;
}

.risk-metrics {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 24px;
  align-items: center;
  max-width: 500px;
  margin: 0 auto 20px;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.metric-label {
  font-size: 14px;
  color: var(--apple-text-secondary);
  min-width: 80px;
}

.metric-value {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.metric-value :deep(.el-progress) {
  flex: 1;
}

.score-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--apple-text);
  min-width: 60px;
}

.metric-value-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--apple-primary);
}

.goal-match {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--apple-bg);
  border-radius: 12px;
  font-size: 14px;
  color: var(--apple-text-secondary);
}

.goal-match strong {
  color: var(--apple-text);
}

/* 配置卡片 */
.allocation-card {
  padding: 28px;
}

.allocation-chart {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  align-items: center;
  margin-bottom: 24px;
}

.chart-container {
  display: flex;
  justify-content: center;
}

.pie-chart {
  width: 280px;
  height: 280px;
}

.allocation-legend {
  display: grid;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  background: var(--apple-bg);
  border-radius: 10px;
}

.legend-color {
  width: 14px;
  height: 14px;
  border-radius: 4px;
}

.legend-name {
  flex: 1;
  font-size: 14px;
  color: var(--apple-text);
}

.legend-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--apple-text);
}

.allocation-notes {
  padding: 20px;
  background: var(--apple-bg);
  border-radius: 14px;
}

.notes-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--apple-text);
  margin-bottom: 12px;
}

.notes-list {
  list-style: none;
  display: grid;
  gap: 10px;
}

.notes-list li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 14px;
  color: var(--apple-text-secondary);
}

.notes-list li .el-icon {
  color: var(--apple-primary);
  margin-top: 2px;
}

/* 市场调整 */
.market-options {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.market-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: var(--apple-bg);
  border: 2px solid transparent;
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.market-option:hover {
  border-color: var(--apple-border);
}

.market-option.active {
  border-color: var(--apple-primary);
  background: rgba(0, 122, 255, 0.05);
}

.market-icon-large {
  font-size: 32px;
  color: var(--apple-primary);
}

.market-name {
  font-size: 16px;
  font-weight: 600;
  color: var(--apple-text);
}

.market-desc {
  font-size: 12px;
  color: var(--apple-text-secondary);
  text-align: center;
}

.adjustment-result {
  padding: 20px;
  background: var(--apple-bg);
  border-radius: 14px;
}

.adjustment-result h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--apple-text);
  margin-bottom: 16px;
}

.adjustment-comparison {
  display: grid;
  gap: 12px;
}

.comparison-item {
  display: grid;
  grid-template-columns: 100px 1fr auto;
  align-items: center;
  gap: 16px;
}

.asset-name {
  font-size: 14px;
  color: var(--apple-text);
}

.adjustment-bar {
  position: relative;
  height: 8px;
  background: var(--apple-border);
  border-radius: 4px;
  overflow: hidden;
}

.original-bar {
  position: absolute;
  height: 100%;
  background: var(--apple-text-tertiary);
  border-radius: 4px;
  opacity: 0.3;
}

.adjusted-bar {
  position: absolute;
  height: 100%;
  background: var(--apple-primary);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.adjustment-values {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.adjustment-values .original {
  color: var(--apple-text-tertiary);
  text-decoration: line-through;
}

.adjustment-values .adjusted {
  font-weight: 600;
}

.adjustment-values .adjusted.up {
  color: #34C759;
}

.adjustment-values .adjusted.down {
  color: #FF3B30;
}

.adjustment-reason {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--apple-border);
  font-size: 13px;
  color: var(--apple-text-secondary);
}

/* 操作按钮 */
.result-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 8px 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .smart-allocation-page {
    padding: 16px;
  }

  .page-title {
    font-size: 28px;
  }

  .allocation-chart {
    grid-template-columns: 1fr;
  }

  .pie-chart {
    width: 240px;
    height: 240px;
  }

  .market-options {
    grid-template-columns: 1fr;
  }

  .comparison-item {
    grid-template-columns: 80px 1fr auto;
  }
}
</style>
