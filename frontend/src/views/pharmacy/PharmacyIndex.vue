<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getMedicineList,
  getMedicineDetail,
  createMedicine,
  updateMedicine,
  deleteMedicine
} from '@/api/pharmacy'

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
    min_stock: 0
  }
})

const rules = {
  medicine_no: [{ required: true, message: '请输入药品编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入药品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入单价', trigger: 'blur' }]
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
          min_stock: form.inventory.min_stock
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
  <div class="pharmacy-index">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">药房管理</h1>
      <el-button type="primary" @click="handleOpenCreate">新增药品</el-button>
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
        stripe
        border
        class="w-full"
      >
        <el-table-column prop="id" label="ID" width="80" />
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
    >
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
          <el-form-item label="分类">
            <el-input v-model="form.category" placeholder="请输入药品分类" />
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
</style>
