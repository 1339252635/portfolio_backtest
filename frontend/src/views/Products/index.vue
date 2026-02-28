<template>
  <div class="products-page">
    <el-card class="apple-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <div class="search-box">
              <el-icon class="search-icon"><Search /></el-icon>
              <input
                v-model="searchQuery"
                placeholder="搜索产品名称或代码"
                class="apple-search-input"
              />
            </div>
            <el-select v-model="filterType" placeholder="产品类型" clearable class="apple-select">
              <el-option label="ETF" value="ETF" />
              <el-option label="基金" value="基金" />
              <el-option label="混合型" value="混合型" />
            </el-select>
          </div>
          <div class="header-right">
            <button class="apple-btn primary" @click="showAddDialog = true">
              <el-icon><Plus /></el-icon>
              <span>添加产品</span>
            </button>
            <button class="apple-btn secondary" @click="syncSelected">
              <el-icon><Refresh /></el-icon>
              <span>同步数据</span>
            </button>
            <button class="apple-btn secondary" @click="initDefaults">
              <el-icon><Download /></el-icon>
              <span>初始化默认</span>
            </button>
          </div>
        </div>
      </template>

      <el-table
        v-loading="productsStore.loading"
        :data="filteredProducts"
        class="apple-table"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="code" label="产品代码" width="120" />
        <el-table-column prop="name" label="产品名称" />
        <el-table-column prop="type" label="类型" width="100">
          <template #default="{ row }">
            <span class="apple-tag" :class="row.type === 'ETF' ? 'blue' : 'green'">{{ row.type }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="fee_rate" label="管理费率" width="100">
          <template #default="{ row }">
            {{ (row.fee_rate * 100).toFixed(2) }}%
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewData(row)">查看数据</el-button>
            <el-button link type="primary" @click="editProduct(row)">编辑</el-button>
            <el-button link type="danger" @click="deleteProduct(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="filteredProducts.length"
          layout="total, sizes, prev, pager, next"
        />
      </div>
    </el-card>

    <!-- 添加/编辑产品对话框 -->
    <el-dialog
      v-model="showAddDialog"
      :title="isEditing ? '编辑产品' : '添加产品'"
      width="500px"
      class="apple-dialog"
    >
      <el-form :model="productForm" label-width="100px" class="apple-form">
        <el-form-item label="产品代码" required>
          <el-input v-model="productForm.code" :disabled="isEditing" class="apple-input" />
        </el-form-item>
        <el-form-item label="产品名称" required>
          <el-input v-model="productForm.name" class="apple-input" />
        </el-form-item>
        <el-form-item label="产品类型" required>
          <el-select v-model="productForm.type" class="apple-select-full">
            <el-option label="ETF" value="ETF" />
            <el-option label="基金" value="基金" />
            <el-option label="混合型" value="混合型" />
          </el-select>
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="productForm.category" class="apple-input" />
        </el-form-item>
        <el-form-item label="管理费率">
          <el-input-number v-model="productForm.fee_rate" :min="0" :max="1" :step="0.001" class="apple-input-number" />
        </el-form-item>
        <el-form-item label="申购费率">
          <el-input-number v-model="productForm.purchase_fee" :min="0" :max="1" :step="0.001" class="apple-input-number" />
        </el-form-item>
        <el-form-item label="赎回费率">
          <el-input-number v-model="productForm.redemption_fee" :min="0" :max="1" :step="0.001" class="apple-input-number" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="productForm.description" type="textarea" rows="3" class="apple-textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="apple-btn secondary" @click="showAddDialog = false">取消</button>
        <button class="apple-btn primary" @click="saveProduct">确定</button>
      </template>
    </el-dialog>

    <!-- 查看数据对话框 -->
    <el-dialog
      v-model="showDataDialog"
      title="历史数据"
      width="800px"
      class="apple-dialog"
    >
      <div v-if="currentProduct" class="data-dialog-header">
        <div class="product-title">
          <span class="product-name">{{ currentProduct.name }}</span>
          <span class="product-code">{{ currentProduct.code }}</span>
        </div>
        <button class="apple-btn primary" @click="syncCurrentProduct">
          <el-icon><Refresh /></el-icon>
          <span>同步最新数据</span>
        </button>
      </div>
      <el-table :data="priceData" height="400" v-loading="dataLoading" class="apple-table">
        <el-table-column prop="date" label="日期" width="120" />
        <el-table-column prop="nav" label="净值" width="100" />
        <el-table-column prop="close" label="收盘价" width="100" />
        <el-table-column prop="open" label="开盘价" width="100" />
        <el-table-column prop="high" label="最高价" width="100" />
        <el-table-column prop="low" label="最低价" width="100" />
        <el-table-column prop="volume" label="成交量" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useProductsStore } from '@/stores/products'
import { ElMessage, ElMessageBox } from 'element-plus'
import { productApi } from '@/api'

const productsStore = useProductsStore()

const searchQuery = ref('')
const filterType = ref('')
const currentPage = ref(1)
const pageSize = ref(20)
const selectedProducts = ref([])
const showAddDialog = ref(false)
const showDataDialog = ref(false)
const isEditing = ref(false)
const currentProduct = ref(null)
const priceData = ref([])
const dataLoading = ref(false)

const productForm = ref({
  code: '',
  name: '',
  type: 'ETF',
  category: '',
  fee_rate: 0,
  purchase_fee: 0,
  redemption_fee: 0,
  description: ''
})

const filteredProducts = computed(() => {
  let result = productsStore.products
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(p => 
      p.name.toLowerCase().includes(query) || 
      p.code.toLowerCase().includes(query)
    )
  }
  
  if (filterType.value) {
    result = result.filter(p => p.type === filterType.value)
  }
  
  return result
})

const handleSelectionChange = (selection) => {
  selectedProducts.value = selection
}

const saveProduct = async () => {
  try {
    if (isEditing.value) {
      await productsStore.updateProduct(currentProduct.value.id, productForm.value)
      ElMessage.success('更新成功')
    } else {
      await productsStore.createProduct(productForm.value)
      ElMessage.success('添加成功')
    }
    showAddDialog.value = false
    resetForm()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

const editProduct = (product) => {
  isEditing.value = true
  currentProduct.value = product
  productForm.value = { ...product }
  showAddDialog.value = true
}

const deleteProduct = async (product) => {
  try {
    await ElMessageBox.confirm(`确定删除产品 ${product.name} 吗？`, '提示', {
      type: 'warning'
    })
    await productsStore.deleteProduct(product.id)
    ElMessage.success('删除成功')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const viewData = async (product) => {
  currentProduct.value = product
  showDataDialog.value = true
  dataLoading.value = true
  
  try {
    const response = await productApi.getData(product.code)
    priceData.value = response
  } catch (error) {
    ElMessage.error('获取数据失败')
  } finally {
    dataLoading.value = false
  }
}

const syncCurrentProduct = async () => {
  if (!currentProduct.value) return
  
  dataLoading.value = true
  try {
    await productsStore.syncProductData([currentProduct.value.code])
    await viewData(currentProduct.value)
    ElMessage.success('同步成功')
  } catch (error) {
    ElMessage.error('同步失败')
  } finally {
    dataLoading.value = false
  }
}

const syncSelected = async () => {
  if (selectedProducts.value.length === 0) {
    ElMessage.warning('请选择要同步的产品')
    return
  }
  
  const codes = selectedProducts.value.map(p => p.code)
  try {
    await productsStore.syncProductData(codes)
    ElMessage.success('同步成功')
  } catch (error) {
    ElMessage.error('同步失败')
  }
}

const initDefaults = async () => {
  try {
    await productsStore.initDefaultProducts()
    await productsStore.fetchProducts()
    ElMessage.success('初始化成功')
  } catch (error) {
    ElMessage.error('初始化失败')
  }
}

const resetForm = () => {
  productForm.value = {
    code: '',
    name: '',
    type: 'ETF',
    category: '',
    fee_rate: 0,
    purchase_fee: 0,
    redemption_fee: 0,
    description: ''
  }
  isEditing.value = false
  currentProduct.value = null
}

onMounted(() => {
  productsStore.fetchProducts()
})
</script>

<style scoped>
.products-page {
  padding: 0;
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

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-box {
  position: relative;
  width: 280px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #86868b;
  z-index: 1;
}

.apple-search-input {
  width: 100%;
  height: 40px;
  padding: 0 12px 0 40px;
  border: none;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.04);
  font-size: 14px;
  color: #1d1d1f;
  transition: all 0.2s ease;
}

.apple-search-input:focus {
  outline: none;
  background: rgba(0, 0, 0, 0.06);
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1);
}

.apple-search-input::placeholder {
  color: #86868b;
}

.apple-select {
  width: 140px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.apple-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 10px;
  border: none;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.apple-btn.primary {
  background: linear-gradient(135deg, #0071e3 0%, #42a5f5 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 113, 227, 0.3);
}

.apple-btn.primary:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 16px rgba(0, 113, 227, 0.4);
}

.apple-btn.secondary {
  background: rgba(0, 0, 0, 0.04);
  color: #1d1d1f;
}

.apple-btn.secondary:hover {
  background: rgba(0, 0, 0, 0.08);
}

.apple-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.apple-tag.blue {
  background: rgba(0, 113, 227, 0.1);
  color: #0071e3;
}

.apple-tag.green {
  background: rgba(52, 199, 89, 0.1);
  color: #34c759;
}

.apple-table {
  background: transparent;
}

.apple-table :deep(th) {
  font-weight: 600;
  color: #86868b;
  background: rgba(0, 0, 0, 0.02);
}

.pagination {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.apple-dialog :deep(.el-dialog) {
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.apple-dialog :deep(.el-dialog__header) {
  padding: 24px 24px 0;
}

.apple-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
}

.apple-dialog :deep(.el-dialog__body) {
  padding: 24px;
}

.apple-dialog :deep(.el-dialog__footer) {
  padding: 0 24px 24px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.apple-form :deep(.el-form-item__label) {
  color: #1d1d1f;
  font-weight: 500;
}

.apple-input :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 10px;
  box-shadow: none;
}

.apple-input :deep(.el-input__wrapper:hover) {
  background: rgba(0, 0, 0, 0.06);
}

.apple-input :deep(.el-input__wrapper.is-focus) {
  background: white;
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1);
}

.apple-select-full {
  width: 100%;
}

.apple-select-full :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 10px;
  box-shadow: none;
}

.apple-input-number :deep(.el-input__wrapper) {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 10px;
  box-shadow: none;
}

.apple-textarea :deep(.el-textarea__inner) {
  background: rgba(0, 0, 0, 0.04);
  border-radius: 10px;
  border: none;
  box-shadow: none;
  padding: 12px;
}

.apple-textarea :deep(.el-textarea__inner:focus) {
  background: white;
  box-shadow: 0 0 0 4px rgba(0, 113, 227, 0.1);
}

.data-dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.product-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.product-name {
  font-size: 18px;
  font-weight: 600;
  color: #1d1d1f;
}

.product-code {
  font-size: 14px;
  color: #86868b;
}
</style>
