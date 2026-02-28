import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { productApi } from '@/api'

export const useProductsStore = defineStore('products', () => {
  // State
  const products = ref([])
  const loading = ref(false)
  const currentProduct = ref(null)

  // Getters
  const productList = computed(() => products.value)
  const etfProducts = computed(() => products.value.filter(p => p.type === 'ETF'))
  const fundProducts = computed(() => products.value.filter(p => p.type !== 'ETF'))

  // Actions
  const fetchProducts = async (params = {}) => {
    loading.value = true
    try {
      const response = await productApi.getList(params)
      products.value = response.items || []
      return response
    } catch (error) {
      console.error('Failed to fetch products:', error)
      throw error
    } finally {
      loading.value = false
    }
  }

  const createProduct = async (data) => {
    const response = await productApi.create(data)
    products.value.push(response)
    return response
  }

  const updateProduct = async (id, data) => {
    const response = await productApi.update(id, data)
    const index = products.value.findIndex(p => p.id === id)
    if (index !== -1) {
      products.value[index] = response
    }
    return response
  }

  const deleteProduct = async (id) => {
    await productApi.delete(id)
    products.value = products.value.filter(p => p.id !== id)
  }

  const syncProductData = async (codes) => {
    return await productApi.sync(codes)
  }

  const initDefaultProducts = async () => {
    return await productApi.initDefaults()
  }

  return {
    products,
    loading,
    currentProduct,
    productList,
    etfProducts,
    fundProducts,
    fetchProducts,
    createProduct,
    updateProduct,
    deleteProduct,
    syncProductData,
    initDefaultProducts
  }
})
