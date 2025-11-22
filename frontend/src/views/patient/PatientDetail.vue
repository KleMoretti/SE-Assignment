<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getPatientDetail } from '@/api/patient'
// 引入图标
import { User, Edit, ArrowLeft } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const patientId = computed(() => route.params.id)
const patient = ref(null)
const loading = ref(false)
const activeTab = ref('info')

// 加载病人数据
const loadPatientData = async () => {
  loading.value = true
  try {
    const res = await getPatientDetail(patientId.value)
    if (res.success) {
      patient.value = res.data
    } else {
      ElMessage.error(res.message || '加载病人数据失败')
    }
  } catch (error) {
    ElMessage.error('请求失败，请检查网络')
  } finally {
    loading.value = false
  }
}

// 跳转到编辑页面
const goToEdit = () => {
  router.push({ name: 'PatientEdit', params: { id: patientId.value } })
}

// 返回上一页
const goBack = () => {
  router.push({ name: 'PatientList' })
}

// 生命周期
onMounted(() => {
  loadPatientData()
})
</script>

<template>
  <el-card class="box-card" v-loading="loading">
    <!-- 头部 -->
    <template #header>
      <div class="flex justify-between items-center">
        <span class="text-xl font-semibold flex items-center">
          <el-icon class="mr-2"><User /></el-icon>
          <span>病人详情: {{ patient?.name }}</span>
        </span>
        <div>
          <el-button :icon="Edit" type="primary" @click="goToEdit">编辑</el-button>
          <el-button :icon="ArrowLeft" @click="goBack">返回列表</el-button>
        </div>
      </div>
    </template>

    <div v-if="patient">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="info">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="病人编号">{{ patient.patient_no }}</el-descriptions-item>
            <el-descriptions-item label="姓名">{{ patient.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ patient.gender }}</el-descriptions-item>
            <el-descriptions-item label="年龄">{{ patient.age }}</el-descriptions-item>
            <el-descriptions-item label="身份证号">{{ patient.id_card }}</el-descriptions-item>
            <el-descriptions-item label="联系电话">{{ patient.phone }}</el-descriptions-item>
            <el-descriptions-item label="住址" :span="2">{{ patient.address }}</el-descriptions-item>
            <el-descriptions-item label="紧急联系人">{{ patient.emergency_contact }}</el-descriptions-item>
            <el-descriptions-item label="紧急联系电话">{{ patient.emergency_phone }}</el-descriptions-item>
            <el-descriptions-item label="创建时间">{{ patient.created_at }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ patient.updated_at }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <el-tab-pane label="病历记录" name="records">
          <div class="p-4 text-gray-500">病历记录功能待开发...</div>
        </el-tab-pane>

        <el-tab-pane label="预约记录" name="appointments">
          <div class="p-4 text-gray-500">预约记录功能待开发...</div>
        </el-tab-pane>
      </el-tabs>
    </div>
    <div v-else class="text-center text-gray-500 p-8">
      未能加载病人信息。
    </div>
  </el-card>
</template>

<style scoped>
.el-descriptions {
  margin-top: 20px;
}
</style>

