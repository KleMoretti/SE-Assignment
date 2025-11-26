<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { Memo, ArrowLeft, Search } from '@element-plus/icons-vue'
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
  router.push('/pharmacy/inventory')
}

const goToPurchase = () => {
  router.push('/pharmacy/purchase')
}

onMounted(() => {
  fetchData()
})
</script>

<template>
  <div class="catalog-container">
    <!-- 欢迎区域 -->
    <div class="page-header">
      <div class="header-content">
        <div class="back-button" @click="router.push('/pharmacy')">
          <el-icon><ArrowLeft /></el-icon>
          <span>返回</span>
        </div>
        <div class="header-title">
          <el-icon class="title-icon"><Memo /></el-icon>
          <h1>药品目录</h1>
        </div>
        <p class="header-subtitle">查看所有药品的详细信息</p>
      </div>
      <div v-if="userStore.isAdmin" class="header-actions">
        <el-button @click="goToInventory">库存监控</el-button>
        <el-button @click="goToPurchase">采购管理</el-button>
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
        <el-select
          v-model="categoryFilter"
          placeholder="按药品分类筛选"
          clearable
          size="large"
          class="category-select"
        >
          <el-option
            v-for="category in categoryOptions"
            :key="category"
            :label="category"
            :value="category"
          />
        </el-select>
        <el-button type="primary" size="large" @click="handleSearch">搜索</el-button>
      </div>
    </div>

    <!-- 药品列表 -->
    <div class="table-card">
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
.catalog-container {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 20px;
  padding-bottom: 40px;
}

/* 页面头部 */
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 30px 40px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
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

/* 搜索卡片 */
.search-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  animation: fadeInUp 0.6s ease-out;
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

.category-select {
  width: 200px;
}

/* 表格卡片 */
.table-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  animation: fadeInUp 0.6s ease-out 0.1s backwards;
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

  .search-content {
    flex-direction: column;
  }

  .search-input,
  .category-select {
    width: 100%;
  }
}
</style>
