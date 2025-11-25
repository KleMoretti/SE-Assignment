<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { getMedicineList, getMedicineDetail } from '@/api/pharmacy'

const loading = ref(false)
const medicines = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const categoryFilter = ref('')

const detailVisible = ref(false)
const detailLoading = ref(false)
const currentMedicine = ref(null)

const router = useRouter()
const userStore = useUserStore()

const categoryOptions = computed(() => {
  const set = new Set()
  medicines.value.forEach((item) => {
    if (item.inventory && item.category) {
      set.add(item.category)
    }
  })
  return Array.from(set)
})

const displayedMedicines = computed(() => {
  let list = medicines.value.filter((item) => item.inventory)
  if (categoryFilter.value) {
    list = list.filter((item) => item.category === categoryFilter.value)
  }
  return list
})

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

const goToInventory = () => {
  router.push('/pharmacy')
}

const goToPurchase = () => {
  router.push('/pharmacy/purchase')
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="pharmacy-catalog">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-800">药品信息</h1>
        <p class="text-gray-500 text-sm mt-1">查看库存中的药品信息</p>
      </div>
      <div v-if="userStore.isAdmin" class="flex gap-2">
        <el-button @click="goToInventory">库存管理</el-button>
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
        <el-select
          v-model="categoryFilter"
          placeholder="按药品分类筛选"
          clearable
          class="w-48"
        >
          <el-option
            v-for="category in categoryOptions"
            :key="category"
            :label="category"
            :value="category"
          />
        </el-select>
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-sm">
      <el-table
        v-loading="loading"
        :data="displayedMedicines"
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
        <el-table-column prop="status" label="状态" width="100" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleShowDetail(row)">
              详情
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
  </div>
</template>

<style scoped>
.pharmacy-catalog {
  padding: 20px;
}
</style>
