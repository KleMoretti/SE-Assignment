<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { DocumentCopy, ArrowLeft, Plus, Search } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import {
  getMedicineList,
  getMedicineDetail,
  createMedicine,
  updateMedicine,
  deleteMedicine
} from '@/api/pharmacy'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const medicines = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')

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
})
</script>

<template>
  <div class="inventory-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="back-button" @click="router.push('/pharmacy')">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回</span>
        </div>
        <div class="header-title">
          <el-icon class="title-icon"><DocumentCopy /></el-icon>
          <h1>库存监控</h1>
        </div>
        <p class="header-subtitle">管理药品库存，监控预警信息</p>
      </div>
      <div class="header-actions">
        <el-button v-if="userStore.isAdmin" type="primary" @click="handleOpenCreate">
          <el-icon><Plus /></el-icon>
          新增药品
        </el-button>
      </div>
    </div>

    <!-- 预警说明 -->
    <div class="alert-info">
      <div class="alert-item">
        <div class="alert-badge expired"></div>
        <span>红色高亮：药品已过期</span>
      </div>
      <div class="alert-item">
        <div class="alert-badge near-expiry"></div>
        <span>橙色高亮：药品即将过期（30天内）</span>
      </div>
      <div class="alert-item">
        <div class="alert-badge low-stock"></div>
        <span>黄色高亮：库存不足</span>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-card">
      <div class="search-content">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索药品名称/编号/通用名"
          clearable
          size="large"
          class="search-input"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" @click="handleSearch">搜索</el-button>
      </div>
    </div>

    <!-- 药品列表 -->
    <div class="table-card">
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

    <!-- 详情抽屉 -->
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

    <!-- 新增/编辑对话框 -->
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
.inventory-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  padding-bottom: 40px;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #42e695 0%, #3bb2b8 100%);
  border-radius: 16px;
  padding: 30px 40px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(66, 230, 149, 0.3);
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

/* 预警说明 */
.alert-info {
  background: white;
  border-radius: 12px;
  padding: 16px 24px;
  margin-bottom: 20px;
  display: flex;
  gap: 32px;
  flex-wrap: wrap;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  animation: fadeInUp 0.6s ease-out;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.alert-badge {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.alert-badge.expired {
  background: #ffe6e6;
  border: 2px solid #f56c6c;
}

.alert-badge.near-expiry {
  background: #fff3e0;
  border: 2px solid #e6a23c;
}

.alert-badge.low-stock {
  background: #fff7e6;
  border: 2px solid #e6a23c;
}

/* 搜索卡片 */
.search-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  animation: fadeInUp 0.6s ease-out 0.1s backwards;
}

.search-content {
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 280px;
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

  .alert-info {
    flex-direction: column;
    gap: 12px;
  }

  .search-content {
    flex-direction: column;
  }

  .search-input {
    width: 100%;
  }
}
</style>
