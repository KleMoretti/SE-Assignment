<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import {
  getMedicineList,
  getMedicineDetail,
  createMedicine,
  updateMedicine,
  deleteMedicine,
  getMedicationRequestList,
  approveMedicationRequest,
  rejectMedicationRequest
} from '@/api/pharmacy'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const medicines = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')

const requestLoading = ref(false)
const medicationRequests = ref([])
const requestTotal = ref(0)
const requestPage = ref(1)
const requestPageSize = ref(10)
const requestStatus = ref('PENDING')

const detailVisible = ref(false)
const detailLoading = ref(false)
const currentMedicine = ref(null)

const dialogVisible = ref(false)
const dialogTitle = ref('新增药品')
const isEdit = ref(false)
const formLoading = ref(false)

const formRef = ref()
const form = reactive({
  id: null,
  medicine_no: '',
  name: '',
  generic_name: '',
  category: '',
  specification: '',
  unit: '',
  manufacturer: '',
  price: null,
  prescription_required: false,
  usage: '',
  indications: '',
  contraindications: '',
  side_effects: '',
  storage_conditions: '',
  status: 'active',
  inventory: {
    quantity: 0,
    min_stock: 0,
    production_date: '',
    expiry_date: ''
  }
})

const rules = {
  medicine_no: [{ required: true, message: '请输入药品编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入药品名称', trigger: 'blur' }],
  category: [{ required: true, message: '请输入药品分类', trigger: 'blur' }],
  price: [{ required: true, message: '请输入单价', trigger: 'blur' }],
  'inventory.production_date': [
    { required: true, message: '请选择生产日期', trigger: 'change' }
  ],
  'inventory.expiry_date': [
    { required: true, message: '请选择过期日期', trigger: 'change' }
  ]
}

const resetForm = () => {
  form.id = null
  form.medicine_no = ''
  form.name = ''
  form.generic_name = ''
  form.category = ''
  form.specification = ''
  form.unit = ''
  form.manufacturer = ''
  form.price = null
  form.prescription_required = false
  form.usage = ''
  form.indications = ''
  form.contraindications = ''
  form.side_effects = ''
  form.storage_conditions = ''
  form.status = 'active'
  form.inventory.quantity = 0
  form.inventory.min_stock = 0
  form.inventory.production_date = ''
  form.inventory.expiry_date = ''
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getMedicineList({
      page: page.value,
      per_page: pageSize.value,
      search: searchKeyword.value
    })
    if (res.success && res.data) {
      medicines.value = res.data.items || []
      total.value = res.data.total || 0
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  fetchData()
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchData()
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  page.value = 1
  fetchData()
}

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
    fetchData()
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

const isLowStock = (row) => {
  const inventory = row.inventory
  if (!inventory) return false
  const quantity = inventory.quantity ?? 0
  const minStock = inventory.min_stock ?? 0
  return minStock > 0 && quantity < minStock
}

const getExpiryDiffDays = (row) => {
  const inventory = row.inventory
  if (!inventory || !inventory.expiry_date) return null
  const expDate = new Date(inventory.expiry_date)
  if (Number.isNaN(expDate.getTime())) return null
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const diffMs = expDate.getTime() - today.getTime()
  return Math.ceil(diffMs / (1000 * 60 * 60 * 24))
}

const isExpired = (row) => {
  const diff = getExpiryDiffDays(row)
  return diff !== null && diff < 0
}

const isNearExpiry = (row) => {
  const diff = getExpiryDiffDays(row)
  return diff !== null && diff >= 0 && diff <= 30
}

const tableRowClassName = ({ row }) => {
  // 已过期 - 最高优先级，红色高亮
  if (isExpired(row)) {
    return 'expired-row'
  }
  // 即将过期 - 次高优先级，橙色高亮
  if (isNearExpiry(row)) {
    return 'near-expiry-row'
  }
  // 库存不足 - 黄色高亮
  if (isLowStock(row)) {
    return 'low-stock-row'
  }
  return ''
}

const goToInfo = () => {
  router.push('/pharmacy/info')
}

const goToPurchase = () => {
  router.push('/pharmacy/purchase')
}

const handleShowDetail = async (row) => {
  detailVisible.value = true
  detailLoading.value = true
  try {
    const res = await getMedicineDetail(row.id)
    if (res.success) {
      currentMedicine.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取详情失败')
  } finally {
    detailLoading.value = false
  }
}

const handleOpenCreate = () => {
  resetForm()
  isEdit.value = false
  dialogTitle.value = '新增药品'
  dialogVisible.value = true
}

const handleOpenEdit = (row) => {
  resetForm()
  isEdit.value = true
  dialogTitle.value = '编辑药品'
  form.id = row.id
  form.medicine_no = row.medicine_no
  form.name = row.name
  form.generic_name = row.generic_name
  form.category = row.category
  form.specification = row.specification
  form.unit = row.unit
  form.manufacturer = row.manufacturer
  form.price = row.price
  form.prescription_required = row.prescription_required
  form.usage = row.usage
  form.indications = row.indications
  form.contraindications = row.contraindications
  form.side_effects = row.side_effects
  form.storage_conditions = row.storage_conditions
  form.status = row.status
  form.inventory.quantity = row.inventory?.quantity ?? 0
  form.inventory.min_stock = row.inventory?.min_stock ?? 0
  form.inventory.production_date = row.inventory?.production_date || ''
  form.inventory.expiry_date = row.inventory?.expiry_date || ''
  dialogVisible.value = true
}

const handleSubmit = () => {
  if (!formRef.value) return
  formRef.value.validate(async (valid) => {
    if (!valid) return
    formLoading.value = true
    try {
      const payload = {
        medicine_no: form.medicine_no,
        name: form.name,
        generic_name: form.generic_name,
        category: form.category,
        specification: form.specification,
        unit: form.unit,
        manufacturer: form.manufacturer,
        price: form.price,
        prescription_required: form.prescription_required,
        usage: form.usage,
        indications: form.indications,
        contraindications: form.contraindications,
        side_effects: form.side_effects,
        storage_conditions: form.storage_conditions,
        status: form.status,
        inventory: {
          quantity: form.inventory.quantity,
          min_stock: form.inventory.min_stock,
          production_date: form.inventory.production_date,
          expiry_date: form.inventory.expiry_date
        }
      }

      if (isEdit.value && form.id) {
        await updateMedicine(form.id, payload)
        ElMessage.success('更新成功')
      } else {
        await createMedicine(payload)
        ElMessage.success('创建成功')
      }
      dialogVisible.value = false
      fetchData()
    } catch (error) {
      ElMessage.error('保存失败')
    } finally {
      formLoading.value = false
    }
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该药品吗？', '提示', {
      type: 'warning'
    })
    await deleteMedicine(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  fetchData()
  fetchRequests()
})
</script>

<template>
  <div class="pharmacy-index">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">药品管理</h1>
        <p class="text-gray-500 text-sm mt-1">管理药品信息、库存和采购</p>
      </div>
      <div class="flex gap-2">
        <el-button v-if="userStore.isAdmin" type="primary" @click="handleOpenCreate">
          新增药品
        </el-button>
        <el-button @click="goToInfo">药品信息</el-button>
        <el-button @click="goToPurchase">采购管理</el-button>
      </div>
    </div>

    <div class="bg-white p-4 rounded-lg shadow-sm mb-4">
      <div class="flex gap-4 items-center">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索药品名称/编号/通用名"
          clearable
          class="w-72"
          @keyup.enter="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-sm">
      <el-table
        v-loading="loading"
        :data="medicines"
        :row-class-name="tableRowClassName"
        stripe
        border
        class="w-full"
      >
        <el-table-column prop="medicine_no" label="药品编号" width="140" />
        <el-table-column prop="name" label="药品名称" />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="specification" label="规格" width="120" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="manufacturer" label="生产厂家" />
        <el-table-column prop="price" label="单价(元)" width="120" />
        <el-table-column label="库存数量" width="120">
          <template #default="{ row }">
            {{ row.inventory?.quantity ?? 0 }}
          </template>
        </el-table-column>
        <el-table-column label="生产日期" width="140">
          <template #default="{ row }">
            {{ row.inventory?.production_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="过期日期" width="140">
          <template #default="{ row }">
            {{ row.inventory?.expiry_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="预警" width="220">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-1">
              <el-tag
                v-if="isExpired(row)"
                type="danger"
                size="small"
              >
                ⚠ 过期！
              </el-tag>
              <el-tag
                v-else-if="isNearExpiry(row)"
                type="warning"
                size="small"
              >
                ⚠ 即将过期
              </el-tag>
              <el-tag
                v-if="isLowStock(row)"
                type="warning"
                size="small"
              >
                ⚠ 库存不足
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="260" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleShowDetail(row)">
              详情
            </el-button>
            <el-button type="warning" size="small" @click="handleOpenEdit(row)">
              编辑
            </el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="p-4 flex justify-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>

    <div v-if="userStore.isAdmin" class="mt-8">
      <div class="flex justify-between items-center mb-4">
        <div>
          <h2 class="text-xl font-semibold text-gray-800">用药申请审核</h2>
          <p class="text-gray-500 text-sm mt-1">查看并处理待审核的用药申请</p>
        </div>
        <div class="flex items-center gap-3">
          <el-select
            v-model="requestStatus"
            size="small"
            class="w-40"
            @change="handleRequestStatusChange"
          >
            <el-option label="待审核" value="PENDING" />
            <el-option label="已通过" value="APPROVED" />
            <el-option label="已拒绝" value="REJECTED" />
          </el-select>
          <el-button size="small" @click="fetchRequests">刷新</el-button>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-sm">
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
              <div>{{ row.status }}</div>
              <div v-if="row.reason" class="text-gray-500 text-xs truncate">
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

    <el-drawer
      v-model="detailVisible"
      title="药品详情"
      size="50%"
    >
      <div v-if="detailLoading" class="flex justify-center items-center h-40 text-gray-500">
        加载中...
      </div>
      <div v-else-if="currentMedicine" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <div class="text-gray-500 text-sm">药品编号</div>
            <div class="text-gray-900 font-medium">{{ currentMedicine.medicine_no }}</div>
          </div>
          <div>
            <div class="text-gray-500 text-sm">药品名称</div>
            <div class="text-gray-900 font-medium">{{ currentMedicine.name }}</div>
          </div>
          <div>
            <div class="text-gray-500 text-sm">通用名称</div>
            <div class="text-gray-900 font-medium">{{ currentMedicine.generic_name }}</div>
          </div>
          <div>
            <div class="text-gray-500 text-sm">分类</div>
            <div class="text-gray-900 font-medium">{{ currentMedicine.category }}</div>
          </div>
          <div>
            <div class="text-gray-500 text-sm">规格</div>
            <div class="text-gray-900 font-medium">{{ currentMedicine.specification }}</div>
          </div>
          <div>
            <div class="text-gray-500 text-sm">单位</div>
            <div class="text-gray-900 font-medium">{{ currentMedicine.unit }}</div>
          </div>
          <div>
            <div class="text-gray-500 text-sm">生产厂家</div>
            <div class="text-gray-900 font-medium">{{ currentMedicine.manufacturer }}</div>
          </div>
          <div>
            <div class="text-gray-500 text-sm">单价(元)</div>
            <div class="text-gray-900 font-medium">{{ currentMedicine.price }}</div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <div class="text-gray-500 text-sm">是否处方药</div>
            <div class="text-gray-900 font-medium">
              {{ currentMedicine.prescription_required ? '是' : '否' }}
            </div>
          </div>
          <div>
            <div class="text-gray-500 text-sm">状态</div>
            <div class="text-gray-900 font-medium">{{ currentMedicine.status }}</div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <div class="text-gray-500 text-sm">库存数量</div>
            <div class="text-gray-900 font-medium">
              {{ currentMedicine.inventory?.quantity ?? 0 }}
            </div>
          </div>
          <div>
            <div class="text-gray-500 text-sm">库存下限</div>
            <div class="text-gray-900 font-medium">
              {{ currentMedicine.inventory?.min_stock ?? 0 }}
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <div class="text-gray-500 text-sm">生产日期</div>
            <div class="text-gray-900 font-medium">
              {{ currentMedicine.inventory?.production_date || '-' }}
            </div>
          </div>
          <div>
            <div class="text-gray-500 text-sm">过期日期</div>
            <div class="text-gray-900 font-medium">
              {{ currentMedicine.inventory?.expiry_date || '-' }}
            </div>
          </div>
        </div>

        <div>
          <div class="text-gray-500 text-sm mb-1">用法用量</div>
          <div class="text-gray-900 whitespace-pre-line">
            {{ currentMedicine.usage }}
          </div>
        </div>
        <div>
          <div class="text-gray-500 text-sm mb-1">适应症</div>
          <div class="text-gray-900 whitespace-pre-line">
            {{ currentMedicine.indications }}
          </div>
        </div>
        <div>
          <div class="text-gray-500 text-sm mb-1">禁忌症</div>
          <div class="text-gray-900 whitespace-pre-line">
            {{ currentMedicine.contraindications }}
          </div>
        </div>
        <div>
          <div class="text-gray-500 text-sm mb-1">副作用</div>
          <div class="text-gray-900 whitespace-pre-line">
            {{ currentMedicine.side_effects }}
          </div>
        </div>
        <div>
          <div class="text-gray-500 text-sm mb-1">储存条件</div>
          <div class="text-gray-900 whitespace-pre-line">
            {{ currentMedicine.storage_conditions }}
          </div>
        </div>
      </div>
    </el-drawer>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      destroy-on-close
      class="medicine-dialog"
      top="5vh"
    >
      <div class="dialog-form-scroll">
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          :disabled="formLoading"
        >
        <div class="grid grid-cols-2 gap-x-6">
          <el-form-item label="药品编号" prop="medicine_no">
            <el-input v-model="form.medicine_no" placeholder="请输入药品编号" />
          </el-form-item>
          <el-form-item label="药品名称" prop="name">
            <el-input v-model="form.name" placeholder="请输入药品名称" />
          </el-form-item>
          <el-form-item label="通用名称">
            <el-input v-model="form.generic_name" placeholder="请输入通用名称" />
          </el-form-item>
          <el-form-item label="分类" prop="category">
            <el-select v-model="form.category" placeholder="请选择药品分类" class="w-full">
              <el-option label="抗感染药" value="抗感染药" />
              <el-option label="镇痛/解热/抗炎药" value="镇痛/解热/抗炎药" />
              <el-option label="心血管用药" value="心血管用药" />
              <el-option label="抗凝/抗血小板药" value="抗凝/抗血小板药" />
              <el-option label="消化系统药" value="消化系统药" />
              <el-option label="呼吸系统药" value="呼吸系统药" />
              <el-option label="内分泌与代谢药" value="内分泌与代谢药" />
              <el-option label="激素与免疫抑制剂" value="激素与免疫抑制剂" />
              <el-option label="肿瘤化疗药" value="肿瘤化疗药" />
              <el-option label="精神神经用药" value="精神神经用药" />
              <el-option label="过敏/急救用药" value="过敏/急救用药" />
              <el-option label="维生素与营养制剂" value="维生素与营养制剂" />
              <el-option label="局部用药" value="局部用药" />
              <el-option label="疫苗与血液制品" value="疫苗与血液制品" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>
          <el-form-item label="规格">
            <el-input v-model="form.specification" placeholder="如：0.25g*24片" />
          </el-form-item>
          <el-form-item label="单位">
            <el-input v-model="form.unit" placeholder="如：盒、瓶" />
          </el-form-item>
          <el-form-item label="生产厂家">
            <el-input v-model="form.manufacturer" placeholder="请输入生产厂家" />
          </el-form-item>
          <el-form-item label="单价(元)" prop="price">
            <el-input v-model.number="form.price" type="number" placeholder="请输入单价" />
          </el-form-item>
          <el-form-item label="是否处方药">
            <el-switch v-model="form.prescription_required" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="form.status" placeholder="请选择状态" class="w-full">
              <el-option label="启用" value="active" />
              <el-option label="停用" value="inactive" />
            </el-select>
          </el-form-item>
          <el-form-item label="库存数量">
            <el-input
              v-model.number="form.inventory.quantity"
              type="number"
              placeholder="当前库存数量"
            />
          </el-form-item>
          <el-form-item label="库存下限">
            <el-input
              v-model.number="form.inventory.min_stock"
              type="number"
              placeholder="低库存预警值"
            />
          </el-form-item>
          <el-form-item label="生产日期" prop="inventory.production_date">
            <el-date-picker
              v-model="form.inventory.production_date"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="请选择生产日期"
              class="w-full"
            />
          </el-form-item>
          <el-form-item label="过期日期" prop="inventory.expiry_date">
            <el-date-picker
              v-model="form.inventory.expiry_date"
              type="date"
              value-format="YYYY-MM-DD"
              placeholder="请选择过期日期"
              class="w-full"
            />
          </el-form-item>
        </div>

        <el-form-item label="用法用量">
          <el-input
            v-model="form.usage"
            type="textarea"
            :rows="2"
            placeholder="请输入用法用量"
          />
        </el-form-item>
        <el-form-item label="适应症">
          <el-input
            v-model="form.indications"
            type="textarea"
            :rows="2"
            placeholder="请输入适应症"
          />
        </el-form-item>
        <el-form-item label="禁忌症">
          <el-input
            v-model="form.contraindications"
            type="textarea"
            :rows="2"
            placeholder="请输入禁忌症"
          />
        </el-form-item>
        <el-form-item label="副作用">
          <el-input
            v-model="form.side_effects"
            type="textarea"
            :rows="2"
            placeholder="请输入可能的副作用"
          />
        </el-form-item>
        <el-form-item label="储存条件">
          <el-input
            v-model="form.storage_conditions"
            type="textarea"
            :rows="2"
            placeholder="请输入储存条件"
          />
        </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" :loading="formLoading" @click="handleSubmit">
            保 存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.pharmacy-index {
  padding: 20px;
}

.medicine-dialog {
  max-width: 700px;
  max-height: 70vh;
  display: flex;
  flex-direction: column;
}

.medicine-dialog :deep(.el-dialog__body) {
  flex: 1;
  overflow-y: auto;
}

.dialog-form-scroll {
  padding-right: 4px;
}

/* 已过期 - 红色高亮 */
:deep(.el-table__row.expired-row) {
  background-color: #ffe6e6 !important;
}

:deep(.el-table__row.expired-row > td) {
  background-color: #ffe6e6 !important;
}

:deep(.el-table__row.expired-row:hover > td) {
  background-color: #ffcccc !important;
}

/* 即将过期 - 橙色高亮 */
:deep(.el-table__row.near-expiry-row) {
  background-color: #fff3e0 !important;
}

:deep(.el-table__row.near-expiry-row > td) {
  background-color: #fff3e0 !important;
}

:deep(.el-table__row.near-expiry-row:hover > td) {
  background-color: #ffe0b3 !important;
}

/* 库存不足 - 黄色高亮 */
:deep(.el-table__row.low-stock-row) {
  background-color: #fff7e6 !important;
}

:deep(.el-table__row.low-stock-row > td) {
  background-color: #fff7e6 !important;
}

:deep(.el-table__row.low-stock-row:hover > td) {
  background-color: #ffe6b3 !important;
}
</style>
