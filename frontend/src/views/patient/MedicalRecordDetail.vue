<template>
  <div class="medical-record-detail-container">
    <div class="page-header">
      <el-page-header @back="goBack">
        <template #content>
          <div class="header-content">
            <h1 class="page-title">
              <el-icon class="title-icon"><Document /></el-icon>
              病历详情
            </h1>
          </div>
        </template>
      </el-page-header>
    </div>

    <el-card v-loading="loading" class="detail-card" shadow="never">
      <template v-if="record">
        <!-- 基本信息 -->
        <div class="section">
          <h3 class="section-title">基本信息</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="病历号">
              {{ record.recordNo || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="病人姓名">
              {{ record.patientName || record.patient_name || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="主治医生">
              {{ record.doctorName || record.doctor_name || '—' }}
            </el-descriptions-item>
            <el-descriptions-item label="就诊日期">
              {{ formatDate(record.visitDate || record.visit_date || record.diagnosis_date) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 诊断信息 -->
        <div class="section">
          <h3 class="section-title">诊断信息</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="主诉症状">
              <div class="text-content">{{ record.symptoms || '无记录' }}</div>
            </el-descriptions-item>
            <el-descriptions-item label="诊断结果">
              <div class="text-content">{{ record.diagnosis || '—' }}</div>
            </el-descriptions-item>
            <el-descriptions-item label="治疗方案">
              <div class="text-content">{{ record.treatment || '无记录' }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 处方信息 -->
        <div class="section" v-if="record.prescription">
          <h3 class="section-title">处方信息</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="药品处方">
              <div class="text-content prescription-text">{{ record.prescription }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 备注信息 -->
        <div class="section" v-if="record.notes">
          <h3 class="section-title">备注</h3>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="备注信息">
              <div class="text-content">{{ record.notes }}</div>
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 时间信息 -->
        <div class="section">
          <h3 class="section-title">记录时间</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="创建时间">
              {{ formatDateTime(record.createdAt || record.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ formatDateTime(record.updatedAt || record.updated_at) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </template>

      <el-empty v-else-if="!loading" description="未找到病历记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import { getMedicalRecordDetail } from '@/api/patient'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const record = ref(null)

const formatDate = (value) => {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

const formatDateTime = (value) => {
  if (!value) return '—'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return value
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  const s = String(d.getSeconds()).padStart(2, '0')
  return `${y}-${m}-${day} ${h}:${min}:${s}`
}

const fetchDetail = async () => {
  const recordId = route.params.id
  if (!recordId) {
    ElMessage.error('病历ID无效')
    goBack()
    return
  }

  loading.value = true
  try {
    const res = await getMedicalRecordDetail(recordId)
    record.value = res.data || null
  } catch (error) {
    console.error('加载病历详情失败:', error)
    ElMessage.error('加载病历详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.go(-1)
}

onMounted(() => {
  fetchDetail()
})
</script>

<style scoped>
.medical-record-detail-container {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-header {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  font-size: 26px;
  color: #409eff;
}

.detail-card {
  margin-bottom: 20px;
}

.section {
  margin-bottom: 24px;
}

.section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 12px 0;
  padding-bottom: 8px;
  border-bottom: 2px solid #409eff;
}

.text-content {
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.6;
  color: #606266;
}

.prescription-text {
  font-family: 'Courier New', monospace;
  background-color: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
}
</style>
