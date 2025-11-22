<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPatientList, createPatient, updatePatient, deletePatient } from '@/api/patient'
import { Search, Plus, Edit, Delete, InfoFilled } from '@element-plus/icons-vue'

const router = useRouter()

// 响应式数据
const tableData = ref([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const editingPatient = ref(null)
const patientFormRef = ref(null)

const total = ref(0)
const queryParams = ref({
  page: 1,
  per_page: 10,
  search: ''
})

const formData = reactive({
  name: '',
  gender: '男',
  age: null,
  phone: '',
  id_card: '',
  address: ''
})

const formRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  id_card: [
    { required: true, message: '请输入身份证号', trigger: 'blur' },
    {
      pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/,
      message: '请输入正确的身份证号',
      trigger: 'blur'
    }
  ]
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const res = await getPatientList(queryParams.value)
    if (res.success) {
      tableData.value = res.data.items
      total.value = res.data.total
    } else {
      ElMessage.error(res.message || '加载数据失败')
    }
  } catch (error) {
    ElMessage.error('请求失败，请检查网络')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  queryParams.value.page = 1
  fetchData()
}

// 分页大小改变
const handleSizeChange = (newSize) => {
  queryParams.value.per_page = newSize
  fetchData()
}

// 当前页改变
const handleCurrentChange = (newPage) => {
  queryParams.value.page = newPage
  fetchData()
}

// 显示新增弹窗
const showAddDialog = () => {
  editingPatient.value = null
  resetFormData()
  dialogVisible.value = true
}

// 显示编辑弹窗
const showEditDialog = (patient) => {
  editingPatient.value = patient
  Object.assign(formData, {
    name: patient.name,
    gender: patient.gender,
    age: patient.age,
    phone: patient.phone,
    id_card: patient.id_card,
    address: patient.address
  })
  dialogVisible.value = true
}

// 提交表单
const submitPatient = async () => {
  if (!patientFormRef.value) return

  await patientFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (editingPatient.value) {
        await updatePatient(editingPatient.value.id, formData)
        ElMessage.success('更新病人信息成功')
      } else {
        await createPatient(formData)
        ElMessage.success('添加病人成功')
      }
      closeDialog()
      fetchData()
    } catch (error) {
      ElMessage.error(editingPatient.value ? '更新失败' : '添加失败')
    } finally {
      submitting.value = false
    }
  })
}

// 关闭弹窗
const closeDialog = () => {
  dialogVisible.value = false
  resetFormData()
}

// 重置表单
const resetFormData = () => {
  Object.assign(formData, {
    name: '',
    gender: '男',
    age: null,
    phone: '',
    id_card: '',
    address: ''
  })
  if (patientFormRef.value) {
    patientFormRef.value.clearValidate()
  }
}

// 跳转到详情页面
const goToDetail = (id) => {
  router.push({ name: 'PatientDetail', params: { id } })
}

// 删除
const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('此操作将永久删除该病人及其所有关联记录，是否继续？', '危险操作', {
      confirmButtonText: '确认删除',
      cancelButtonText: '取消',
      type: 'warning',
      icon: Delete
    })
    await deletePatient(id)
    ElMessage.success('删除成功')
    // 如果当前页只剩一条数据，删除后返回上一页
    if (tableData.value.length === 1 && queryParams.value.page > 1) {
      queryParams.value.page--
    }
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + (error.message || '未知错误'))
    }
  }
}

// 生命周期
onMounted(() => {
  fetchData()
})
</script>

<template>
  <div>
    <!-- 搜索区域 -->
    <div class="mb-4">
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="关键字">
          <el-input
            v-model="queryParams.search"
            placeholder="病人姓名、编号、电话"
            clearable
            style="width: 240px"
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Plus" @click="showAddDialog">新增病人</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 表格区域 -->
    <el-table v-loading="loading" :data="tableData" border stripe style="width: 100%">
      <el-table-column prop="patient_no" label="病人编号" width="140" fixed />
      <el-table-column prop="name" label="姓名" width="120" fixed />
      <el-table-column prop="gender" label="性别" width="80" />
      <el-table-column prop="age" label="年龄" width="80" />
      <el-table-column prop="phone" label="联系电话" width="150" />
      <el-table-column prop="id_card" label="身份证号" width="200" />
      <el-table-column prop="address" label="住址" min-width="250" show-overflow-tooltip />

      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button-group>
            <el-tooltip content="查看详情" placement="top">
              <el-button type="primary" :icon="InfoFilled" size="small" @click="goToDetail(row.id)" />
            </el-tooltip>
            <el-tooltip content="编辑" placement="top">
              <el-button type="warning" :icon="Edit" size="small" @click="showEditDialog(row)" />
            </el-tooltip>
            <el-tooltip content="删除" placement="top">
              <el-button type="danger" :icon="Delete" size="small" @click="handleDelete(row.id)" />
            </el-tooltip>
          </el-button-group>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页区域 -->
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

  <!-- 添加/编辑病人对话框 -->
  <el-dialog
    v-model="dialogVisible"
    :title="editingPatient ? '编辑病人' : '新增病人'"
    width="600px"
    :close-on-click-modal="false"
  >
    <el-form
      ref="patientFormRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="姓名" prop="name">
            <el-input v-model="formData.name" placeholder="请输入姓名" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="formData.gender">
              <el-radio label="男">男</el-radio>
              <el-radio label="女">女</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-col>
      </el-row>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="年龄" prop="age">
            <el-input-number v-model="formData.age" :min="0" :max="120" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系电话" prop="phone">
            <el-input v-model="formData.phone" placeholder="请输入联系电话" />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="身份证号" prop="id_card">
        <el-input v-model="formData.id_card" placeholder="请输入身份证号" />
      </el-form-item>

      <el-form-item label="住址" prop="address">
        <el-input
          v-model="formData.address"
          type="textarea"
          :rows="2"
          placeholder="请输入详细住址"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="closeDialog">取消</el-button>
      <el-button type="primary" @click="submitPatient" :loading="submitting">
        确定
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.el-form--inline .el-form-item {
  margin-bottom: 0;
}
</style>
