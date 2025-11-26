<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Memo, ShoppingCart, DocumentCopy, Warning, House, ArrowRight, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getMedicineList, getMedicationRequestList } from '@/api/pharmacy'

const router = useRouter()
const userStore = useUserStore()

const goBack = () => {
  router.push({ name: 'Home' })
}

const loading = ref(false)
const stats = ref({
  totalMedicines: 0,
  lowStockCount: 0,
  expiredCount: 0,
  nearExpiryCount: 0,
  pendingRequests: 0
})

const goToCatalog = () => {
  router.push('/pharmacy/info')
}

const goToInventory = () => {
  router.push('/pharmacy/inventory')
}

const goToPurchase = () => {
  router.push('/pharmacy/purchase')
}

const goToRequests = () => {
  router.push('/pharmacy/requests')
}

const isLowStock = (item) => {
  const inventory = item.inventory
  if (!inventory) return false
  const quantity = inventory.quantity ?? 0
  const minStock = inventory.min_stock ?? 0
  return minStock > 0 && quantity < minStock
}

const isExpired = (item) => {
  const inventory = item.inventory
  if (!inventory || !inventory.expiry_date) return false
  const expDate = new Date(inventory.expiry_date)
  if (Number.isNaN(expDate.getTime())) return false
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const diffMs = expDate.getTime() - today.getTime()
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))
  return diffDays < 0
}

const isNearExpiry = (item) => {
  const inventory = item.inventory
  if (!inventory || !inventory.expiry_date) return false
  const expDate = new Date(inventory.expiry_date)
  if (Number.isNaN(expDate.getTime())) return false
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const diffMs = expDate.getTime() - today.getTime()
  const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24))
  return diffDays >= 0 && diffDays <= 30
}

const fetchStats = async () => {
  loading.value = true
  try {
    const medicineRes = await getMedicineList({ page: 1, per_page: 1000 })
    if (medicineRes.success && medicineRes.data) {
      const medicines = medicineRes.data.items || []
      stats.value.totalMedicines = medicines.length
      stats.value.lowStockCount = medicines.filter(isLowStock).length
      stats.value.expiredCount = medicines.filter(isExpired).length
      stats.value.nearExpiryCount = medicines.filter(isNearExpiry).length
    } else {
      console.error('获取药品列表失败:', medicineRes)
    }

    if (userStore.isAdmin) {
      const requestRes = await getMedicationRequestList({ status: 'PENDING', page: 1, per_page: 1000 })
      if (requestRes.success && requestRes.data) {
        stats.value.pendingRequests = requestRes.data.total || 0
      } else {
        console.error('获取用药申请失败:', requestRes)
      }
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
    const errorMsg = error.response?.data?.message || error.message || '加载统计数据失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchStats()
})
</script>

<template>
  <div class="pharmacy-container">
    <!-- 返回按钮 -->
    <div class="back-button-container">
      <el-button 
        :icon="ArrowLeft" 
        @click="goBack" 
        circle 
        class="index-back-button"
      />
    </div>

    <!-- 欢迎标题 -->
    <div class="welcome-section">
      <h1 class="welcome-title">
        <el-icon class="title-icon"><House /></el-icon>
        药品管理系统
      </h1>
      <p class="welcome-subtitle">统一管理药品信息、库存和采购</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid" v-loading="loading">
      <div class="stat-card">
        <div class="stat-icon medicine-icon">
          <el-icon><Memo /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">药品总数</div>
          <div class="stat-value">{{ stats.totalMedicines }}</div>
        </div>
      </div>

      <div class="stat-card warning-card" v-if="stats.lowStockCount > 0">
        <div class="stat-icon warning-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">库存不足</div>
          <div class="stat-value">{{ stats.lowStockCount }}</div>
        </div>
      </div>

      <div class="stat-card expired-card" v-if="stats.expiredCount > 0">
        <div class="stat-icon expired-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">已过期</div>
          <div class="stat-value">{{ stats.expiredCount }}</div>
        </div>
      </div>

      <div class="stat-card alert-card" v-if="stats.nearExpiryCount > 0">
        <div class="stat-icon alert-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">即将过期</div>
          <div class="stat-value">{{ stats.nearExpiryCount }}</div>
        </div>
      </div>

      <div class="stat-card request-card" v-if="userStore.isAdmin && stats.pendingRequests > 0">
        <div class="stat-icon request-icon">
          <el-icon><DocumentCopy /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">待审核申请</div>
          <div class="stat-value">{{ stats.pendingRequests }}</div>
        </div>
      </div>
    </div>

    <!-- 功能卡片网格 -->
    <div class="service-grid">
      <div class="service-card" @click="goToCatalog">
        <div class="card-icon catalog-icon">
          <el-icon><Memo /></el-icon>
        </div>
        <h3 class="card-title">药品目录</h3>
        <p class="card-description">查看所有药品的详细信息</p>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="service-card" @click="goToInventory">
        <div class="card-icon inventory-icon">
          <el-icon><DocumentCopy /></el-icon>
        </div>
        <h3 class="card-title">库存监控</h3>
        <p class="card-description">查看药品库存和预警信息</p>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div class="service-card" @click="goToPurchase">
        <div class="card-icon purchase-icon">
          <el-icon><ShoppingCart /></el-icon>
        </div>
        <h3 class="card-title">采购管理</h3>
        <p class="card-description">管理药品采购和收货入库</p>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>

      <div v-if="userStore.isAdmin" class="service-card" @click="goToRequests">
        <div class="card-icon request-icon">
          <el-icon><DocumentCopy /></el-icon>
        </div>
        <h3 class="card-title">用药审核</h3>
        <p class="card-description">审核医生的用药申请</p>
        <div class="card-arrow">
          <el-icon><ArrowRight /></el-icon>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pharmacy-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  padding-bottom: 40px;
  box-sizing: border-box;
}

/* 返回按钮容器 */
.back-button-container {
  padding: 20px 0 0 20px;
  animation: fadeIn 0.5s ease-out;
}

.index-back-button {
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.index-back-button:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.3);
}

/* 欢迎区域 */
.welcome-section {
  text-align: center;
  margin-bottom: 40px;
  padding-top: 20px;
  animation: fadeInDown 0.6s ease-out;
}

.welcome-title {
  color: #2c3e50;
  font-size: 36px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.title-icon {
  font-size: 36px;
  color: #67c23a;
}

.welcome-subtitle {
  color: #606266;
  font-size: 16px;
  margin-top: 10px;
  font-weight: 400;
}

/* 统计卡片 */
.stats-grid {
  display: flex;
  justify-content: center;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto 40px;
  flex-wrap: wrap;
}

.stat-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px 30px;
  min-width: 200px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e4e7ed;
  animation: fadeInUp 0.6s ease-out backwards;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.expired-card {
  border-color: #f56c6c;
  background: #fff5f5;
}

.expired-card:hover {
  box-shadow: 0 4px 12px rgba(245, 108, 108, 0.3);
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.medicine-icon {
  background: #ecf5ff;
  color: #409eff;
}

.warning-icon {
  background: #fef0f0;
  color: #f56c6c;
}

.expired-icon {
  background: #ffe6e6;
  color: #f56c6c;
}

.alert-icon {
  background: #fff3e0;
  color: #e6a23c;
}

.request-icon {
  background: #f0f9ff;
  color: #67c23a;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

/* 服务卡片网格 */
.service-grid {
  display: flex;
  justify-content: center;
  align-items: stretch;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
  flex-wrap: wrap;
}

.service-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 35px 25px;
  width: 280px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e4e7ed;
  position: relative;
  animation: fadeInUp 0.6s ease-out backwards;
}

.service-card:nth-child(1) {
  animation-delay: 0.1s;
}

.service-card:nth-child(2) {
  animation-delay: 0.2s;
}

.service-card:nth-child(3) {
  animation-delay: 0.3s;
}

.service-card:nth-child(4) {
  animation-delay: 0.4s;
}

.service-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 70px;
  height: 70px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin: 0 auto 20px;
  transition: all 0.3s ease;
}

.catalog-icon {
  background: #ecf5ff;
  color: #409eff;
}

.service-card:hover .catalog-icon {
  border-color: #409eff;
}

.inventory-icon {
  background: #f0f9ff;
  color: #67c23a;
}

.service-card:hover .inventory-icon {
  border-color: #67c23a;
}

.purchase-icon {
  background: #fef0f0;
  color: #e6a23c;
}

.service-card:hover .purchase-icon {
  border-color: #e6a23c;
}

.request-icon {
  background: #fdf6ec;
  color: #f56c6c;
}

.service-card:hover .request-icon {
  border-color: #f56c6c;
}

.service-card:hover .card-icon {
  transform: scale(1.05);
}

.card-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 10px 0;
  text-align: center;
}

.card-description {
  font-size: 14px;
  color: #909399;
  margin: 0;
  text-align: center;
  line-height: 1.5;
}

.card-arrow {
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-size: 18px;
  color: #c0c4cc;
  opacity: 0;
  transform: translateX(-5px);
  transition: all 0.3s ease;
}

.service-card:hover .card-arrow {
  opacity: 0.6;
  transform: translateX(0);
  color: #409eff;
}

/* 动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .welcome-title {
    font-size: 28px;
  }

  .title-icon {
    font-size: 28px;
  }

  .welcome-subtitle {
    font-size: 14px;
  }

  .stats-grid {
    flex-direction: column;
    align-items: center;
  }

  .stat-card {
    width: 100%;
    max-width: 400px;
  }

  .service-grid {
    flex-direction: column;
    align-items: center;
  }

  .service-card {
    width: 100%;
    max-width: 400px;
  }
}
</style>
