import { createRouter, createWebHistory } from 'vue-router'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/patient',
    name: 'Patient',
    component: () => import('@/views/patient/PatientList.vue'),
    meta: { title: '病人管理' }
  },
  {
    path: '/doctor',
    name: 'Doctor',
    component: () => import('@/views/doctor/DoctorList.vue'),
    meta: { title: '医生管理' }
  },
  {
    path: '/pharmacy',
    name: 'Pharmacy',
    component: () => import('@/views/pharmacy/PharmacyIndex.vue'),
    meta: { title: '药房管理' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 医院管理系统` : '医院管理系统'
  next()
})

export default router
