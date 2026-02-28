<template>
  <div class="backtest-config">
    <div class="page-header">
      <button class="back-btn" @click="cancel">
        <el-icon size="20"><ArrowLeft /></el-icon>
      </button>
      <div class="header-content">
        <h1 class="page-title">新建回测方案</h1>
        <p class="page-subtitle">配置您的投资组合回测参数</p>
      </div>
    </div>

    <el-card class="apple-card">
      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <!-- 基本信息 -->
        <div class="form-section">
          <h3 class="section-title">
            <span class="section-icon"><el-icon><Document /></el-icon></span>
            基本信息
          </h3>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="方案名称" prop="name">
                <el-input v-model="form.name" placeholder="请输入方案名称" class="apple-input" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="回测区间" prop="dateRange">
                <el-date-picker
                  v-model="form.dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="YYYY-MM-DD"
                  class="apple-date-picker"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="描述">
            <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入方案描述" class="apple-textarea" />
          </el-form-item>
        </div>

        <!-- 资金配置 -->
        <div class="form-section">
          <h3 class="section-title">
            <span class="section-icon"><el-icon><Money /></el-icon></span>
            资金配置
          </h3>
          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="初始金额" prop="initial_amount">
                <div class="input-with-unit">
                  <el-input-number v-model="form.initial_amount" :min="1000" :step="1000" class="apple-input-number" />
                  <span class="unit">元</span>
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="定投策略" prop="investment_strategy">
                <el-select v-model="form.investment_strategy" class="apple-select">
                  <el-option label="不定投" value="none" />
                  <el-option label="定期定额" value="fixed" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8" v-if="form.investment_strategy === 'fixed'">
              <el-form-item label="定投金额">
                <div class="input-with-unit">
                  <el-input-number v-model="form.monthly_amount" :min="100" :step="100" class="apple-input-number" />
                  <span class="unit">元/月</span>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 再平衡策略 -->
        <div class="form-section">
          <h3 class="section-title">
            <span class="section-icon"><el-icon><Refresh /></el-icon></span>
            再平衡策略
          </h3>
          <el-row :gutter="24">
            <el-col :span="8">
              <el-form-item label="策略类型" prop="rebalance_strategy">
                <el-select v-model="form.rebalance_strategy" class="apple-select">
                  <el-option label="不调整" value="none" />
                  <el-option label="定期再平衡" value="periodic" />
                  <el-option label="阈值再平衡" value="threshold" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8" v-if="form.rebalance_strategy === 'periodic'">
              <el-form-item label="再平衡周期">
                <div class="input-with-unit">
                  <el-input-number v-model="form.rebalance_period" :min="1" :max="12" class="apple-input-number" />
                  <span class="unit">月</span>
                </div>
              </el-form-item>
            </el-col>
            <el-col :span="8" v-if="form.rebalance_strategy === 'threshold'">
              <el-form-item label="偏离阈值">
                <div class="input-with-unit">
                  <el-input-number v-model="form.rebalance_threshold" :min="1" :max="50" class="apple-input-number" />
                  <span class="unit">%</span>
                </div>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 资产配置 -->
        <div class="form-section">
          <h3 class="section-title">
            <span class="section-icon"><el-icon><PieChart /></el-icon></span>
            资产配置
            <span class="total-badge" :class="{ 'error': totalRatio !== 100 }">
              总计 {{ totalRatio }}%
            </span>
          </h3>

          <div class="allocation-list">
            <div
              v-for="(allocation, index) in form.allocations"
              :key="index"
              class="allocation-item"
            >
              <div class="allocation-number">{{ index + 1 }}</div>
              <el-select v-model="allocation.product_code" placeholder="选择产品" class="apple-select allocation-product">
                <el-option
                  v-for="product in productList"
                  :key="product.code"
                  :label="product.name"
                  :value="product.code"
                />
              </el-select>
              <div class="allocation-ratio">
                <el-slider v-model="allocation.allocation_ratio" :max="100" show-input class="apple-slider" />
              </div>
              <button class="allocation-delete" @click="removeAllocation(index)">
                <el-icon><Delete /></el-icon>
              </button>
            </div>
          </div>

          <button class="add-allocation-btn" @click="addAllocation">
            <el-icon><Plus /></el-icon>
            <span>添加配置</span>
          </button>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <button class="apple-btn secondary" @click="cancel">取消</button>
          <button class="apple-btn primary" @click="submitForm" :disabled="submitting || totalRatio !== 100">
            <el-icon v-if="submitting" class="is-loading"><Loading /></el-icon>
            <span>{{ submitting ? '创建中...' : '开始回测' }}</span>
          </button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useBacktestStore } from '@/stores/backtest'
import { useProductsStore } from '@/stores/products'

const router = useRouter()
const backtestStore = useBacktestStore()
const productsStore = useProductsStore()

const formRef = ref(null)
const submitting = ref(false)
const productList = ref([])

const form = ref({
  name: '',
  description: '',
  dateRange: [],
  initial_amount: 100000,
  rebalance_strategy: 'none',
  rebalance_period: 12,
  rebalance_threshold: 10,
  investment_strategy: 'none',
  monthly_amount: 5000,
  allocations: [{ product_code: '', allocation_ratio: 0 }]
})

const rules = {
  name: [{ required: true, message: '请输入方案名称', trigger: 'blur' }],
  dateRange: [{ required: true, message: '请选择回测区间', trigger: 'change' }],
  initial_amount: [{ required: true, message: '请输入初始金额', trigger: 'blur' }],
  rebalance_strategy: [{ required: true, message: '请选择再平衡策略', trigger: 'change' }],
  investment_strategy: [{ required: true, message: '请选择定投策略', trigger: 'change' }]
}

const totalRatio = computed(() => {
  return form.value.allocations.reduce((sum, item) => sum + (item.allocation_ratio || 0), 0)
})

const addAllocation = () => {
  form.value.allocations.push({ product_code: '', allocation_ratio: 0 })
}

const removeAllocation = (index) => {
  if (form.value.allocations.length > 1) {
    form.value.allocations.splice(index, 1)
  } else {
    ElMessage.warning('至少需要保留一个配置')
  }
}

const submitForm = async () => {
  if (totalRatio.value !== 100) {
    ElMessage.error('资产配置比例总和必须等于100%')
    return
  }

  const valid = await formRef.value?.validate()
  if (!valid) return

  submitting.value = true
  try {
    const data = {
      ...form.value,
      start_date: form.value.dateRange[0],
      end_date: form.value.dateRange[1]
    }
    delete data.dateRange

    const result = await backtestStore.createBacktest(data)
    ElMessage.success('回测创建成功')
    router.push(`/backtest/result/${result.id}`)
  } catch (error) {
    ElMessage.error('回测创建失败')
  } finally {
    submitting.value = false
  }
}

const cancel = () => {
  router.back()
}

onMounted(async () => {
  try {
    productList.value = await productsStore.fetchProducts()
  } catch (error) {
    ElMessage.error('获取产品列表失败')
  }
})
</script>

<style scoped>
.backtest-config {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.back-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  border: none;
  background: rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #1d1d1f;
}

.back-btn:hover {
  background: rgba(0, 0, 0, 0.08);
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

.form-section {
  margin-bottom: 32px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 17px;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.section-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #0071e3 0%, #42a5f5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.total-badge {
  margin-left: auto;
  padding: 6px 12px;
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
}

.total-badge.error {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

.apple-input :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  box-shadow: none;
  padding: 4px 16px;
}

.apple-input :deep(.el-input__wrapper:hover) {
  background: rgba(0, 0, 0, 0.06);
}

.apple-input :deep(.el-input__wrapper.is-focus) {
  background: white;
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1);
}

.apple-date-picker {
  width: 100%;
}

.apple-date-picker :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  box-shadow: none;
}

.apple-select {
  width: 100%;
}

.apple-select :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  box-shadow: none;
}

.apple-input-number {
  width: 100%;
}

.apple-input-number :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  box-shadow: none;
}

.input-with-unit {
  display: flex;
  align-items: center;
  gap: 8px;
}

.unit {
  color: #86868b;
  font-size: 14px;
}

.apple-textarea :deep(.el-textarea__inner) {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 12px;
  border: none;
  box-shadow: none;
  padding: 12px 16px;
}

.apple-textarea :deep(.el-textarea__inner:focus) {
  background: white;
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1);
}

.allocation-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.allocation-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.02);
  border-radius: 14px;
}

.allocation-number {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: linear-gradient(135deg, #0071e3 0%, #42a5f5 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}

.allocation-product {
  width: 280px;
}

.allocation-ratio {
  flex: 1;
}

.apple-slider :deep(.el-slider__runway) {
  background-color: rgba(0, 0, 0, 0.08);
}

.apple-slider :deep(.el-slider__bar) {
  background: linear-gradient(90deg, #0071e3 0%, #42a5f5 100%);
}

.apple-slider :deep(.el-slider__button) {
  border-color: #0071e3;
  box-shadow: 0 2px 8px rgba(0, 113, 227, 0.3);
}

.allocation-delete {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: #86868b;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.allocation-delete:hover {
  color: #ff3b30;
  background: rgba(255, 59, 48, 0.1);
}

.add-allocation-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 16px;
  margin-top: 12px;
  border: 2px dashed rgba(0, 0, 0, 0.1);
  border-radius: 14px;
  background: transparent;
  color: #0071e3;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.add-allocation-btn:hover {
  border-color: #0071e3;
  background: rgba(0, 113, 227, 0.04);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.apple-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
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

.apple-btn.primary:hover:not(:disabled) {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0, 113, 227, 0.4);
}

.apple-btn.primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.apple-btn.secondary {
  background: rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
}

.apple-btn.secondary:hover {
  background: rgba(0, 0, 0, 0.08);
}
</style>
