<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAppointmentList, cancelAppointment } from '@/api/patient'
import { Search, Plus } from '@element-plus/icons-vue'

const router = useRouter()

// Reactive data
const tableData = ref([])
const loading = ref(false)
const total = ref(0)
const queryParams = ref({
  page: 1,
  per_page: 10,
  search: ''
})

// Fetch data
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getAppointmentList(queryParams.value)
    // axios 封装已返回后端 JSON: { success, message, code, data: { items, total, ... } }
    tableData.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (error) {
    ElMessage.error('加载挂号列表失败')
  } finally {
    loading.value = false
  }
}

// Search
const handleSearch = () => {
  queryParams.value.page = 1
  fetchData()
}

// Pagination
const handleSizeChange = (newSize) => {
  queryParams.value.per_page = newSize
  fetchData()
}

const handleCurrentChange = (newPage) => {
  queryParams.value.page = newPage
  fetchData()
}

const goToAddAppointment = () => {
  router.push({ name: 'AppointmentForm' })
}

// 取消预约
const handleCancelAppointment = async (row) => {
  // 检查预约状态
  if (row.status === 'cancelled') {
    ElMessage.warning('该预约已被取消')
    return
  }
  if (row.status === 'completed') {
    ElMessage.warning('已完成的预约不能取消')
    return
  }

  try {
    await ElMessageBox.confirm(
      `确定要取消预约号为 ${row.appointment_no} 的预约吗？`,
      '取消预约',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await cancelAppointment(row.id)
    ElMessage.success('预约已取消')
    fetchData() // 刷新列表
  } catch (error) {
    if (error !== 'cancel') {
      const errorMsg = error.response?.data?.message || '取消预约失败'
      ElMessage.error(errorMsg)
    }
  }
}

// 查看预约详情
const handleViewDetail = (row) => {
  ElMessageBox.alert(
    `
    <div style="text-align: left;">
      <p><strong>预约号：</strong>${row.appointment_no}</p>
      <p><strong>病人姓名：</strong>${row.patient_name}</p>
      <p><strong>医生姓名：</strong>${row.doctor_name}</p>
      <p><strong>科室：</strong>${row.department}</p>
      <p><strong>预约日期：</strong>${row.appointment_date ? row.appointment_date.split('T')[0] : '-'}</p>
      <p><strong>预约时间：</strong>${row.appointment_time || '-'}</p>
      <p><strong>状态：</strong>${getStatusText(row.status)}</p>
      <p><strong>备注：</strong>${row.notes || '无'}</p>
      <p><strong>创建时间：</strong>${row.created_at ? row.created_at.split('T')[0] + ' ' + row.created_at.split('T')[1].split('.')[0] : '-'}</p>
    </div>
    `,
    '预约详情',
    {
      confirmButtonText: '关闭',
      dangerouslyUseHTMLString: true,
      customClass: 'appointment-detail-dialog'
    }
  )
}

// 获取状态标签类型
const getStatusType = (status) => {
  const statusMap = {
    pending: 'warning',
    confirmed: 'primary',
    completed: 'success',
    cancelled: 'info'
  }
  return statusMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const statusMap = {
    pending: '待确认',
    confirmed: '已确认',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

// Lifecycle
onMounted(() => {
  fetchData()
})
</script>

<template>
  <div>
    <!-- Search Area -->
    <div class="mb-4">
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="关键字">
          <el-input
            v-model="queryParams.search"
            placeholder="病人姓名、医生姓名"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Plus" @click="goToAddAppointment">新增预约</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Table Area -->
    <el-table v-loading="loading" :data="tableData" border stripe style="width: 100%">
      <el-table-column prop="appointment_no" label="预约号" width="120" />
      <el-table-column prop="patient_name" label="病人姓名" min-width="120" />
      <el-table-column prop="doctor_name" label="医生姓名" min-width="120" />
      <el-table-column prop="department" label="科室" min-width="100" />
      <el-table-column label="预约日期" min-width="120">
        <template #default="{ row }">
          {{ row.appointment_date ? row.appointment_date.split('T')[0] : '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="appointment_time" label="预约时间" width="100" />
      <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right" align="center">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleViewDetail(row)">详情</el-button>
          <el-button
            v-if="row.status !== 'completed' && row.status !== 'cancelled'"
            type="danger"
            size="small"
            @click="handleCancelAppointment(row)"
          >
            取消
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div class="mt-6 flex justify-end">
      <el-pagination
        v-model:current-page="queryParams.page"
        v-model:page-size="queryParams.per_page"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<style scoped>
.el-form--inline .el-form-item {
  margin-bottom: 0;
}

:deep(.appointment-detail-dialog) {
  width: 500px;
}

:deep(.appointment-detail-dialog .el-message-box__message p) {
  line-height: 1.8;
  margin: 8px 0;
}
</style>
