<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
import { ShoppingCart, ArrowLeft, DocumentCopy, Clock, Money } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import {
  getMedicineList,
  getPurchaseOrderList,
  createPurchaseOrder,
  getPurchaseOrderDetail,
  receivePurchaseOrder
} from '@/api/pharmacy'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const purchases = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const statusFilter = ref('')
const priorityFilter = ref('')
const stats = ref({ total_purchases: 0, pending_count: 0 })

const createDialogVisible = ref(false)
const createFormLoading = ref(false)
const createFormRef = ref()
const createForm = reactive({
  is_new_medicine: false,
  medicine_id: null,
  medicine_no: '',
  medicine_name: '',
  category: '',
  quantity: null,
  unit_price: null,
  supplier: '',
  purchaser: '',
  expected_delivery_date: '',
  priority: 'medium',
  notes: ''
})

const medicines = ref([])

const receiveDialogVisible = ref(false)
const receiveFormLoading = ref(false)
const receiveFormRef = ref()
const currentPurchase = ref(null)
const receiveForm = reactive({
  batch_no: '',
  production_date: '',
  expiry_date: ''
})

const receiveRules = {
  production_date: [{ required: true, message: '请选择生产日期', trigger: 'change' }],
  expiry_date: [{ required: true, message: '请选择过期日期', trigger: 'change' }]
}

const priorityOptions = [
  { label: '低', value: 'low', type: 'info' },
  { label: '中', value: 'medium', type: 'primary' },
  { label: '高', value: 'high', type: 'danger' }
]

const statusOptions = [
  { label: '全部', value: '' },
  { label: '待处理', value: 'pending' },
  { label: '已完成', value: 'completed' }
]

const validateMedicineSelection = (rule, value, callback) => {
  if (!createForm.is_new_medicine && !value) {
    callback(new Error('请选择已有药品'))
  } else {
    callback()
  }
}

const makeNewMedicineValidator = (label) => {
  return (rule, value, callback) => {
    if (createForm.is_new_medicine && !value) {
      callback(new Error(`请输入${label}`))
    } else {
      callback()
    }
  }
}

const createRules = {
  medicine_id: [{ validator: validateMedicineSelection, trigger: 'change' }],
  medicine_no: [{ validator: makeNewMedicineValidator('药品编号'), trigger: 'blur' }],
  medicine_name: [{ validator: makeNewMedicineValidator('药品名称'), trigger: 'blur' }],
  category: [{ validator: makeNewMedicineValidator('药品分类'), trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }]
}

const fetchMedicines = async () => {
  try {
    const res = await getMedicineList({ page: 1, per_page: 1000, status: 'active' })
    if (res.success && res.data) {
      medicines.value = res.data.items || []
    }
  } catch (error) {
    ElMessage.error('加载药品列表失败')
  }
}

const fetchPurchases = async () => {
  loading.value = true
  try {
    const res = await getPurchaseOrderList({
      page: page.value,
      per_page: pageSize.value,
      status: statusFilter.value,
      priority: priorityFilter.value
    })
    if (res.success && res.data) {
      purchases.value = res.data.items || []
      total.value = res.data.total || 0
      stats.value = res.data.stats || { total_purchases: 0, pending_count: 0 }
    }
  } catch (error) {
    ElMessage.error('加载采购列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  fetchPurchases()
}

const handlePageChange = (newPage) => {
  page.value = newPage
  fetchPurchases()
}

const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  page.value = 1
  fetchPurchases()
}

const getPriorityTagType = (value) => {
  return priorityOptions.find((p) => p.value === value)?.type || 'info'
}

const getPriorityLabel = (value) => {
  return priorityOptions.find((p) => p.value === value)?.label || value || '-'
}

const openCreateDialog = () => {
  resetCreateForm()
  createDialogVisible.value = true
}

const resetCreateForm = () => {
  createForm.is_new_medicine = false
  createForm.medicine_id = null
  createForm.medicine_no = ''
  createForm.medicine_name = ''
  createForm.category = ''
  createForm.quantity = null
  createForm.unit_price = null
  createForm.supplier = ''
  createForm.purchaser = userStore.userInfo?.real_name || userStore.userInfo?.username || ''
  createForm.expected_delivery_date = ''
  createForm.priority = 'medium'
  createForm.notes = ''
}

const handleCreateSubmit = () => {
  if (!createFormRef.value) return
  createFormRef.value.validate(async (valid) => {
    if (!valid) return
    createFormLoading.value = true
    try {
      const payload = { ...createForm }
      const res = await createPurchaseOrder(payload)
      if (res.success) {
        ElMessage.success('采购单创建成功')
        createDialogVisible.value = false
        fetchPurchases()
      }
    } catch (error) {
      ElMessage.error('创建采购单失败')
    } finally {
      createFormLoading.value = false
    }
  })
}

const openReceiveDialog = async (row) => {
  currentPurchase.value = row
  receiveForm.batch_no = row.batch_no || ''
  receiveForm.production_date = row.production_date || ''
  receiveForm.expiry_date = row.expiry_date || ''
  receiveDialogVisible.value = true
}

const handleReceiveSubmit = () => {
  if (!receiveFormRef.value || !currentPurchase.value) return
  receiveFormRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      await ElMessageBox.confirm('确认已收货并入库？', '确认收货', { type: 'warning' })
      receiveFormLoading.value = true
      const payload = { ...receiveForm }
      const res = await receivePurchaseOrder(currentPurchase.value.id, payload)
      if (res.success) {
        ElMessage.success('收货成功，库存已更新')
        receiveDialogVisible.value = false
        fetchPurchases()
      }
    } catch (error) {
      if (error !== 'cancel') {
        ElMessage.error('收货失败')
      }
    } finally {
      receiveFormLoading.value = false
    }
  })
}

const canReceive = (row) => row.status === 'pending'

const totalAmount = computed(() => {
  return purchases.value.reduce((sum, p) => sum + (p.total_price || 0), 0)
})

onMounted(() => {
  fetchMedicines()
  fetchPurchases()
})
</script>

<template>
  <div class="purchase-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="back-button" @click="router.push('/pharmacy')">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回</span>
        </div>
        <div class="header-title">
          <el-icon class="title-icon"><ShoppingCart /></el-icon>
          <h1>药品采购管理</h1>
        </div>
        <p class="header-subtitle">管理采购任务、优先级和收货入库</p>
      </div>
      <div class="header-actions">
        <el-button @click="router.push('/pharmacy/inventory')">库存监控</el-button>
        <el-button @click="router.push('/pharmacy/info')">药品信息</el-button>
        <el-button type="primary" @click="openCreateDialog">新建采购</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon total-icon">
          <el-icon><DocumentCopy /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">采购总数</div>
          <div class="stat-value">{{ stats.total_purchases }}</div>
        </div>
      </div>
      <div class="stat-card pending-card">
        <div class="stat-icon pending-icon">
          <el-icon><Clock /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">待处理采购</div>
          <div class="stat-value">{{ stats.pending_count }}</div>
        </div>
      </div>
      <div class="stat-card amount-card">
        <div class="stat-icon amount-icon">
          <el-icon><Money /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-label">采购总金额</div>
          <div class="stat-value">￥{{ totalAmount.toFixed(2) }}</div>
        </div>
      </div>
    </div>

    <!-- 筛选区域 -->
    <div class="filter-card">
      <el-select
        v-model="statusFilter"
        placeholder="按状态筛选"
        clearable
        class="w-40"
        @change="handleSearch"
      >
        <el-option
          v-for="item in statusOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>

      <el-select
        v-model="priorityFilter"
        placeholder="按优先级筛选"
        clearable
        class="w-40"
        @change="handleSearch"
      >
        <el-option label="全部优先级" :value="''" />
        <el-option
          v-for="item in priorityOptions"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>

      <el-button type="primary" @click="handleSearch">刷新</el-button>
    </div>

    <!-- 采购列表 -->
    <div class="table-card">
      <el-table
        v-loading="loading"
        :data="purchases"
        stripe
        border
        class="w-full"
      >
        <el-table-column prop="purchase_no" label="采购单号" width="180" />
        <el-table-column prop="medicine_name" label="药品" />
        <el-table-column prop="quantity" label="数量" width="90" />
        <el-table-column prop="unit_price" label="单价" width="110">
          <template #default="{ row }">
            ￥{{ row.unit_price?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_price" label="总价" width="120">
          <template #default="{ row }">
            ￥{{ row.total_price?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column label="优先级" width="110">
          <template #default="{ row }">
            <el-tag :type="getPriorityTagType(row.priority)" size="small">
              {{ getPriorityLabel(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column prop="expected_delivery_date" label="预计到货" width="140" />
        <el-table-column prop="actual_delivery_date" label="实际到货" width="140" />
        <el-table-column prop="supplier" label="供应商" />
        <el-table-column prop="purchaser" label="采购员" width="120" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="canReceive(row)"
              type="primary"
              size="small"
              @click="openReceiveDialog(row)"
            >
              确认收货
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="p-4 flex justify-end">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="handlePageChange"
          @size-change="handleSizeChange"
        />
      </div>
    </div>

    <el-dialog
      v-model="createDialogVisible"
      title="新建采购单"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="药品类型">
          <el-radio-group v-model="createForm.is_new_medicine">
            <el-radio-button :label="false">已有药品</el-radio-button>
            <el-radio-button :label="true">新药品</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="!createForm.is_new_medicine" label="药品" prop="medicine_id">
          <el-select
            v-model="createForm.medicine_id"
            placeholder="请选择药品"
            filterable
            class="w-full"
          >
            <el-option
              v-for="m in medicines"
              :key="m.id"
              :label="`${m.medicine_no} - ${m.name}`"
              :value="m.id"
            />
          </el-select>
        </el-form-item>

        <template v-else>
          <el-form-item label="药品编号" prop="medicine_no">
            <el-input v-model="createForm.medicine_no" placeholder="请输入药品编号" />
          </el-form-item>
          <el-form-item label="药品名称" prop="medicine_name">
            <el-input v-model="createForm.medicine_name" placeholder="请输入药品名称" />
          </el-form-item>
          <el-form-item label="分类" prop="category">
            <el-select v-model="createForm.category" placeholder="请选择药品分类" class="w-full">
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
        </template>
        <el-form-item label="数量" prop="quantity">
          <el-input
            v-model.number="createForm.quantity"
            type="number"
            placeholder="请输入采购数量"
          />
        </el-form-item>
        <el-form-item label="单价" prop="unit_price">
          <el-input
            v-model.number="createForm.unit_price"
            type="number"
            placeholder="请输入采购单价"
          />
        </el-form-item>
        <el-form-item label="供应商">
          <el-input v-model="createForm.supplier" placeholder="请输入供应商名称" />
        </el-form-item>
        <el-form-item label="采购员">
          <el-input v-model="createForm.purchaser" placeholder="请输入采购员" />
        </el-form-item>
        <el-form-item label="预计到货">
          <el-date-picker
            v-model="createForm.expected_delivery_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择预计到货日期"
            class="w-full"
          />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="createForm.priority" class="w-full">
            <el-option
              v-for="item in priorityOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="createForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="createDialogVisible = false">取 消</el-button>
          <el-button type="primary" :loading="createFormLoading" @click="handleCreateSubmit">
            保 存
          </el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog
      v-model="receiveDialogVisible"
      title="确认收货"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="receiveFormRef"
        :model="receiveForm"
        :rules="receiveRules"
        label-width="100px"
      >
        <el-form-item label="批次号">
          <el-input v-model="receiveForm.batch_no" placeholder="请输入批次号" />
        </el-form-item>
        <el-form-item label="生产日期" prop="production_date">
          <el-date-picker
            v-model="receiveForm.production_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择生产日期"
            class="w-full"
          />
        </el-form-item>
        <el-form-item label="过期日期" prop="expiry_date">
          <el-date-picker
            v-model="receiveForm.expiry_date"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="请选择过期日期"
            class="w-full"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="receiveDialogVisible = false">取 消</el-button>
          <el-button type="primary" :loading="receiveFormLoading" @click="handleReceiveSubmit">
            确 认
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.purchase-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  padding-bottom: 40px;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  border-radius: 16px;
  padding: 30px 40px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(250, 112, 154, 0.3);
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

.header-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
  animation: fadeInUp 0.6s ease-out;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 1px solid #e4e7ed;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.total-icon {
  background: #ecf5ff;
  color: #409eff;
}

.pending-icon {
  background: #fef0f0;
  color: #e6a23c;
}

.amount-icon {
  background: #f0f9ff;
  color: #67c23a;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

/* 筛选卡片 */
.filter-card {
  background: white;
  border-radius: 12px;
  padding: 20px 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  display: flex;
  gap: 16px;
  align-items: center;
  animation: fadeInUp 0.6s ease-out 0.1s backwards;
}

/* 表格卡片 */
.table-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  animation: fadeInUp 0.6s ease-out 0.2s backwards;
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

/* 对话框 */
.dialog-footer {
  text-align: right;
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

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filter-card {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-card .el-select {
    width: 100%;
  }
}
</style>
