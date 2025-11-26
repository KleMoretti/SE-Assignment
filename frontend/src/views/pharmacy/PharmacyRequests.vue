<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentCopy, ArrowLeft } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import {
  getMedicationRequestList,
  approveMedicationRequest,
  rejectMedicationRequest
} from '@/api/pharmacy'

const router = useRouter()
const userStore = useUserStore()

const requestLoading = ref(false)
const medicationRequests = ref([])
const requestTotal = ref(0)
const requestPage = ref(1)
const requestPageSize = ref(10)
const requestStatus = ref('PENDING')

const fetchRequests = async () => {
  requestLoading.value = true
  try {
    const res = await getMedicationRequestList({
      status: requestStatus.value,
      page: requestPage.value,
      per_page: requestPageSize.value
    })
    if (res.success && res.data) {
      medicationRequests.value = res.data.items || []
      requestTotal.value = res.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载用药申请失败')
  } finally {
    requestLoading.value = false
  }
}

const handleRequestStatusChange = () => {
  requestPage.value = 1
  fetchRequests()
}

const handleRequestPageChange = (newPage) => {
  requestPage.value = newPage
  fetchRequests()
}

const handleRequestSizeChange = (newSize) => {
  requestPageSize.value = newSize
  requestPage.value = 1
  fetchRequests()
}

const handleApproveRequest = async (row) => {
  try {
    await ElMessageBox.confirm('确认通过该用药申请并扣减库存？', '审核确认', {
      type: 'warning'
    })
    await approveMedicationRequest(row.id)
    ElMessage.success('审核通过并已扣减库存')
    fetchRequests()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('审核失败')
    }
  }
}

const handleRejectRequest = async (row) => {
  try {
    const { value } = await ElMessageBox.prompt('请输入拒绝原因', '拒绝用药申请', {
      inputPlaceholder: '如：库存不足或处方不合规',
      inputType: 'textarea',
      confirmButtonText: '确定',
      cancelButtonText: '取消'
    })
    await rejectMedicationRequest(row.id, { reason: value })
    ElMessage.success('已拒绝该用药申请')
    fetchRequests()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('拒绝失败')
    }
  }
}

onMounted(() => {
  fetchRequests()
})
</script>

<template>
  <div class="requests-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="back-button" @click="router.push('/pharmacy')">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回</span>
        </div>
        <div class="header-title">
          <el-icon class="title-icon"><DocumentCopy /></el-icon>
          <h1>用药申请审核</h1>
        </div>
        <p class="header-subtitle">查看并处理医生提交的用药申请</p>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-card">
      <div class="filter-content">
        <div class="filter-label">状态筛选：</div>
        <el-select
          v-model="requestStatus"
          size="large"
          class="status-select"
          @change="handleRequestStatusChange"
        >
          <el-option label="待审核" value="PENDING" />
          <el-option label="已通过" value="APPROVED" />
          <el-option label="已拒绝" value="REJECTED" />
        </el-select>
        <el-button size="large" @click="fetchRequests">刷新</el-button>
      </div>
    </div>

    <!-- 申请列表 -->
    <div class="table-card">
      <el-table
        v-loading="requestLoading"
        :data="medicationRequests"
        stripe
        border
        class="w-full"
      >
        <el-table-column prop="id" label="编号" width="80" />
        <el-table-column prop="created_at" label="申请时间" width="180" />
        <el-table-column prop="patient_name" label="病人" width="140" />
        <el-table-column prop="doctor_name" label="医生" width="140" />
        <el-table-column prop="medicine_name" label="药品" />
        <el-table-column label="用法用量" width="220">
          <template #default="{ row }">
            <div>{{ row.dose || '-' }}</div>
            <div class="text-gray-500 text-xs">{{ row.usage || '' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量" width="90" />
        <el-table-column label="状态/原因" width="200">
          <template #default="{ row }">
            <div>
              <el-tag
                v-if="row.status === 'PENDING'"
                type="warning"
                size="small"
              >
                待审核
              </el-tag>
              <el-tag
                v-else-if="row.status === 'APPROVED'"
                type="success"
                size="small"
              >
                已通过
              </el-tag>
              <el-tag
                v-else-if="row.status === 'REJECTED'"
                type="danger"
                size="small"
              >
                已拒绝
              </el-tag>
            </div>
            <div v-if="row.reason" class="text-gray-500 text-xs truncate mt-1">
              {{ row.reason }}
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'PENDING'"
              type="primary"
              size="small"
              @click="handleApproveRequest(row)"
            >
              通过并发药
            </el-button>
            <el-button
              v-if="row.status === 'PENDING'"
              type="danger"
              size="small"
              @click="handleRejectRequest(row)"
            >
              拒绝
            </el-button>
            <span v-if="row.status !== 'PENDING'" class="text-gray-400 text-sm">
              已处理
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div class="p-4 flex justify-end">
        <el-pagination
          v-model:current-page="requestPage"
          v-model:page-size="requestPageSize"
          :total="requestTotal"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handleRequestPageChange"
          @size-change="handleRequestSizeChange"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.requests-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  padding-bottom: 40px;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 30px 40px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  animation: fadeInDown 0.6s ease-out;
}

.header-content {
  color: white;
}

.back-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  font-size: 14px;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.back-button:hover {
  color: white;
  transform: translateX(-3px);
}

.header-title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.header-title h1 {
  font-size: 32px;
  font-weight: 600;
  margin: 0;
  color: white;
}

.title-icon {
  font-size: 32px;
  color: white;
}

.header-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
  margin: 0;
}

/* 筛选卡片 */
.filter-card {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  animation: fadeInUp 0.6s ease-out;
}

.filter-content {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 15px;
  font-weight: 500;
  color: #606266;
}

.status-select {
  width: 200px;
}

/* 表格卡片 */
.table-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  animation: fadeInUp 0.6s ease-out 0.1s backwards;
}

.table-card :deep(.el-table) {
  border-radius: 12px;
}

.table-card :deep(.el-table th) {
  background: #f5f7fa;
  color: #303133;
  font-weight: 600;
}

.table-card :deep(.el-pagination) {
  padding: 20px;
  justify-content: flex-end;
}

/* 动画 */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    padding: 20px;
  }

  .header-title h1 {
    font-size: 24px;
  }

  .title-icon {
    font-size: 24px;
  }

  .filter-content {
    flex-direction: column;
    align-items: stretch;
  }

  .status-select {
    width: 100%;
  }
}
</style>
