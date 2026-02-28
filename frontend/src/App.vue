<template>
  <el-container class="app-container">
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <div class="logo-icon">
          <el-icon size="28"><TrendCharts /></el-icon>
        </div>
        <span class="logo-text">理财回测</span>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        class="sidebar-menu"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/products">
          <el-icon><Collection /></el-icon>
          <span>产品管理</span>
        </el-menu-item>
        <el-menu-item index="/smart-allocation">
          <el-icon><MagicStick /></el-icon>
          <span>智能配置</span>
        </el-menu-item>
        <el-menu-item index="/backtest">
          <el-icon><DataAnalysis /></el-icon>
          <span>回测中心</span>
        </el-menu-item>
        <el-menu-item index="/analysis">
          <el-icon><TrendCharts /></el-icon>
          <span>数据分析</span>
        </el-menu-item>
      </el-menu>
      
      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            <el-icon size="20"><User /></el-icon>
          </div>
          <span class="user-name">管理员</span>
        </div>
      </div>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1 class="page-title">{{ $route.meta.title || '理财配置回测系统' }}</h1>
        </div>
        <div class="header-right">
          <el-button class="refresh-btn" @click="refreshData">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="apple-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { HomeFilled, Collection, DataAnalysis, TrendCharts, User, Refresh, MagicStick } from '@element-plus/icons-vue'

const route = useRoute()

const refreshData = () => {
  ElMessage.success('数据已刷新')
  window.location.reload()
}
</script>

<style>
@import './styles/apple-theme.css';

.app-container {
  height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
}

.sidebar {
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-right: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
}

.logo {
  height: 80px;
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 12px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
}

.logo-icon {
  width: 44px;
  height: 44px;
  background: linear-gradient(135deg, #0071e3 0%, #42a5f5 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 113, 227, 0.3);
}

.logo-text {
  font-size: 20px;
  font-weight: 600;
  color: var(--apple-text-primary);
  letter-spacing: -0.5px;
}

.sidebar-menu {
  flex: 1;
  padding: 16px 12px;
  border-right: none;
  background: transparent;
}

.sidebar-footer {
  padding: 16px 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--apple-text-primary);
}

.header {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 70px;
  padding: 0 32px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--apple-text-primary);
  letter-spacing: -0.5px;
}

.refresh-btn {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.04);
  border: none;
  color: var(--apple-text-secondary);
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  background: rgba(0, 0, 0, 0.08);
  color: var(--apple-text-primary);
  transform: rotate(180deg);
}

.main-content {
  padding: 32px;
  overflow-y: auto;
}

/* 页面切换动画 */
.apple-fade-enter-active,
.apple-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.apple-fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.apple-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
