<template>
  <div class="doctor-performance-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>医生绩效管理</h2>
      <el-button type="primary" @click="showAddDialog">
        <el-icon><Plus /></el-icon>
        添加绩效评估
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-title">总记录数</div>
          <div class="stat-value">{{ statistics.total_records || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-title">总接诊人数</div>
          <div class="stat-value">{{ statistics.total_patients || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-title">平均满意度</div>
          <div class="stat-value">{{ statistics.average_satisfaction || 0 }}分</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-title">总绩效奖金</div>
          <div class="stat-value">¥{{ statistics.total_bonus || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 搜索栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="医生">
          <el-select
            v-model="searchForm.doctor_id"
            placeholder="请选择医生"
            clearable
            filterable
            @change="handleSearch"
          >
            <el-option
              v-for="doctor in doctors"
              :key="doctor.id"
              :label="`${doctor.name} - ${doctor.department}`"
              :value="doctor.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="年份">
          <el-date-picker
            v-model="searchForm.year"
            type="year"
            placeholder="选择年份"
            format="YYYY"
            value-format="YYYY"
            clearable
            @change="handleSearch"
          />
        </el-form-item>

        <el-form-item label="月份">
          <el-select
            v-model="searchForm.month"
            placeholder="请选择月份"
            clearable
            @change="handleSearch"
          >
            <el-option
              v-for="m in 12"
              :key="m"
              :label="`${m}月`"
              :value="m"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="performanceList"
        stripe
        border
      >
        <el-table-column prop="doctor_name" label="医生姓名" width="120" />
        <el-table-column prop="year" label="年份" width="100" />
        <el-table-column prop="month" label="月份" width="80">
          <template #default="{ row }">
            {{ row.month }}月
          </template>
        </el-table-column>
        <el-table-column prop="patient_count" label="接诊人数" width="100" />
        <el-table-column prop="satisfaction_score" label="满意度评分" width="110">
          <template #default="{ row }">
            <el-rate
              v-model="row.satisfaction_score"
              disabled
              show-score
              text-color="#ff9900"
            />
          </template>
        </el-table-column>
        <el-table-column prop="punctuality_score" label="准时率" width="100">
          <template #default="{ row }">
            {{ row.punctuality_score || 0 }}分
          </template>
        </el-table-column>
        <el-table-column prop="quality_score" label="质量评分" width="100">
          <template #default="{ row }">
            {{ row.quality_score || 0 }}分
          </template>
        </el-table-column>
        <el-table-column prop="total_score" label="综合评分" width="100">
          <template #default="{ row }">
            <el-tag :type="getScoreType(row.total_score)">
              {{ row.total_score ? row.total_score.toFixed(2) : 0 }}分
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="bonus" label="绩效奖金" width="120">
          <template #default="{ row }">
            <span class="bonus-text">¥{{ row.bonus ? row.bonus.toFixed(2) : 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />

        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              link
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-button
              type="primary"
              size="small"
              link
              @click="handleEdit(row)"
            >
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除这条绩效记录吗？"
              @confirm="handleDelete(row.id)"
            >
              <template #reference>
                <el-button
                  type="danger"
                  size="small"
                  link
                >
                  删除
                </el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSearch"
        @current-change="handleSearch"
      />
    </el-card>

    <!-- 添加/编辑绩效对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="performanceFormRef"
        :model="performanceForm"
        :rules="performanceRules"
        label-width="120px"
      >
        <el-form-item label="医生" prop="doctor_id">
          <el-select
            v-model="performanceForm.doctor_id"
            placeholder="请选择医生"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="doctor in doctors"
              :key="doctor.id"
              :label="`${doctor.name} - ${doctor.department} - ${doctor.title}`"
              :value="doctor.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="年份" prop="year">
          <el-date-picker
            v-model="performanceForm.year"
            type="year"
            placeholder="选择年份"
            format="YYYY"
            value-format="YYYY"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="月份" prop="month">
          <el-select
            v-model="performanceForm.month"
            placeholder="请选择月份"
            style="width: 100%"
          >
            <el-option
              v-for="m in 12"
              :key="m"
              :label="`${m}月`"
              :value="m"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="接诊人数" prop="patient_count">
          <el-input-number
            v-model="performanceForm.patient_count"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="满意度评分" prop="satisfaction_score">
          <el-slider
            v-model="performanceForm.satisfaction_score"
            :min="0"
            :max="5"
            :step="0.1"
            show-input
          />
        </el-form-item>

        <el-form-item label="准时率评分" prop="punctuality_score">
          <el-slider
            v-model="performanceForm.punctuality_score"
            :min="0"
            :max="5"
            :step="0.1"
            show-input
          />
        </el-form-item>

        <el-form-item label="质量评分" prop="quality_score">
          <el-slider
            v-model="performanceForm.quality_score"
            :min="0"
            :max="5"
            :step="0.1"
            show-input
          />
        </el-form-item>

        <el-form-item label="备注" prop="notes">
          <el-input
            v-model="performanceForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saveLoading" @click="handleSave">
          保存
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="绩效详情"
      width="700px"
    >
      <el-descriptions v-if="currentPerformance" :column="2" border>
        <el-descriptions-item label="医生姓名">
          {{ currentPerformance.doctor_name }}
        </el-descriptions-item>
        <el-descriptions-item label="评估期间">
          {{ currentPerformance.year }}年{{ currentPerformance.month }}月
        </el-descriptions-item>
        <el-descriptions-item label="接诊人数">
          {{ currentPerformance.patient_count || 0 }} 人
        </el-descriptions-item>
        <el-descriptions-item label="满意度评分">
          <el-rate
            :model-value="currentPerformance.satisfaction_score"
            disabled
            show-score
            text-color="#ff9900"
          />
        </el-descriptions-item>
        <el-descriptions-item label="准时率评分">
          {{ currentPerformance.punctuality_score || 0 }} 分
        </el-descriptions-item>
        <el-descriptions-item label="质量评分">
          {{ currentPerformance.quality_score || 0 }} 分
        </el-descriptions-item>
        <el-descriptions-item label="综合评分">
          <el-tag :type="getScoreType(currentPerformance.total_score)">
            {{ currentPerformance.total_score ? currentPerformance.total_score.toFixed(2) : 0 }} 分
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="绩效奖金">
          <span class="bonus-text-large">
            ¥{{ currentPerformance.bonus ? currentPerformance.bonus.toFixed(2) : 0 }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentPerformance.notes || '无' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import {
  getPerformances,
  getPerformanceDetail,
  createPerformance,
  updatePerformance,
  deletePerformance,
  getPerformanceStatistics,
  getDoctors
} from '@/api/doctor'

const route = useRoute()

// 搜索表单
const searchForm = reactive({
  doctor_id: null,
  year: null,
  month: null
})

// 统计数据
const statistics = ref({})

// 医生列表
const doctors = ref([])

// 绩效列表
const performanceList = ref([])
const loading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  per_page: 10,
  total: 0
})

// 对话框
const dialogVisible = ref(false)
const dialogTitle = ref('添加绩效评估')
const editMode = ref(false)
const saveLoading = ref(false)

// 绩效表单
const performanceFormRef = ref(null)
const performanceForm = reactive({
  id: null,
  doctor_id: null,
  year: null,
  month: null,
  patient_count: 0,
  satisfaction_score: 0,
  punctuality_score: 0,
  quality_score: 0,
  notes: ''
})

// 表单验证规则
const performanceRules = {
  doctor_id: [
    { required: true, message: '请选择医生', trigger: 'change' }
  ],
  year: [
    { required: true, message: '请选择年份', trigger: 'change' }
  ],
  month: [
    { required: true, message: '请选择月份', trigger: 'change' }
  ]
}

// 详情对话框
const detailVisible = ref(false)
const currentPerformance = ref(null)

// 获取绩效列表
const getPerformanceList = async () => {
  loading.value = true
  
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page
    }
    
    // 处理年份参数
    if (searchForm.year) {
      params.year = parseInt(searchForm.year)
    }
    
    if (searchForm.month) {
      params.month = searchForm.month
    }
    
    if (searchForm.doctor_id) {
      params.doctor_id = searchForm.doctor_id
    }
    
    const response = await getPerformances(params)
    
    if (response.success) {
      performanceList.value = response.data.list
      pagination.total = response.data.total
    }
  } catch (error) {
    ElMessage.error(error.message || '获取绩效列表失败')
  } finally {
    loading.value = false
  }
}

// 获取统计数据
const getStatistics = async () => {
  try {
    const params = {}
    
    if (searchForm.year) {
      params.year = parseInt(searchForm.year)
    }
    
    if (searchForm.month) {
      params.month = searchForm.month
    }
    
    const response = await getPerformanceStatistics(params)
    
    if (response.success) {
      statistics.value = response.data
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 获取医生列表
const getDoctorList = async () => {
  try {
    const response = await getDoctors({ per_page: 1000, status: 'active' })
    
    if (response.success) {
      doctors.value = response.data.list
    }
  } catch (error) {
    console.error('获取医生列表失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  getPerformanceList()
  getStatistics()
}

// 重置
const handleReset = () => {
  searchForm.doctor_id = null
  searchForm.year = null
  searchForm.month = null
  handleSearch()
}

// 显示添加对话框
const showAddDialog = () => {
  editMode.value = false
  dialogTitle.value = '添加绩效评估'
  resetForm()
  // 设置默认年月为当前时间
  const now = new Date()
  performanceForm.year = now.getFullYear().toString()
  performanceForm.month = now.getMonth() + 1
  dialogVisible.value = true
}

// 查看详情
const handleView = async (row) => {
  try {
    const response = await getPerformanceDetail(row.id)
    
    if (response.success) {
      currentPerformance.value = response.data
      detailVisible.value = true
    }
  } catch (error) {
    ElMessage.error(error.message || '获取绩效详情失败')
  }
}

// 编辑
const handleEdit = (row) => {
  editMode.value = true
  dialogTitle.value = '编辑绩效评估'
  
  Object.keys(performanceForm).forEach(key => {
    if (key === 'year') {
      performanceForm[key] = row[key]?.toString()
    } else {
      performanceForm[key] = row[key]
    }
  })
  
  dialogVisible.value = true
}

// 删除
const handleDelete = async (id) => {
  try {
    const response = await deletePerformance(id)
    
    if (response.success) {
      ElMessage.success('删除成功')
      getPerformanceList()
      getStatistics()
    }
  } catch (error) {
    ElMessage.error(error.message || '删除失败')
  }
}

// 保存
const handleSave = async () => {
  if (!performanceFormRef.value) return
  
  await performanceFormRef.value.validate(async (valid) => {
    if (!valid) return
    
    saveLoading.value = true
    
    try {
      const { id, ...data } = performanceForm
      
      // 转换年份为数字
      data.year = parseInt(data.year)
      
      let response
      
      if (editMode.value) {
        response = await updatePerformance(id, data)
      } else {
        response = await createPerformance(data)
      }
      
      if (response.success) {
        ElMessage.success(editMode.value ? '更新成功' : '创建成功')
        dialogVisible.value = false
        getPerformanceList()
        getStatistics()
      }
    } catch (error) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      saveLoading.value = false
    }
  })
}

// 关闭对话框
const handleDialogClose = () => {
  resetForm()
  performanceFormRef.value?.clearValidate()
}

// 重置表单
const resetForm = () => {
  Object.assign(performanceForm, {
    id: null,
    doctor_id: null,
    year: null,
    month: null,
    patient_count: 0,
    satisfaction_score: 0,
    punctuality_score: 0,
    quality_score: 0,
    notes: ''
  })
}

// 获取评分类型
const getScoreType = (score) => {
  if (!score) return 'info'
  if (score >= 4.5) return 'success'
  if (score >= 3.5) return 'warning'
  return 'danger'
}

// 初始化
onMounted(() => {
  getDoctorList()
  
  // 从 URL 查询参数中获取 doctor_id
  const route = useRoute()
  if (route.query.doctor_id) {
    searchForm.doctor_id = parseInt(route.query.doctor_id)
  }
  
  getPerformanceList()
  getStatistics()
})
</script>

<style scoped>
.doctor-performance-container {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.search-card {
  margin-bottom: 20px;
}

.table-card {
  margin-bottom: 20px;
}

.el-pagination {
  margin-top: 20px;
  justify-content: flex-end;
}

.bonus-text {
  color: #67c23a;
  font-weight: bold;
}

.bonus-text-large {
  color: #67c23a;
  font-weight: bold;
  font-size: 18px;
}
</style>

