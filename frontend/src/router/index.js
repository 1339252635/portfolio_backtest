import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard/index.vue'
import Products from '@/views/Products/index.vue'
import Backtest from '@/views/Backtest/index.vue'
import BacktestConfig from '@/views/Backtest/Config.vue'
import BacktestResult from '@/views/Backtest/Result.vue'
import Analysis from '@/views/Analysis/index.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { title: '首页' }
  },
  {
    path: '/products',
    name: 'Products',
    component: Products,
    meta: { title: '产品管理' }
  },
  {
    path: '/backtest',
    name: 'Backtest',
    component: Backtest,
    meta: { title: '回测中心' }
  },
  {
    path: '/backtest/config',
    name: 'BacktestConfig',
    component: BacktestConfig,
    meta: { title: '新建回测' }
  },
  {
    path: '/backtest/result/:id',
    name: 'BacktestResult',
    component: BacktestResult,
    meta: { title: '回测结果' }
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis,
    meta: { title: '数据分析' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
