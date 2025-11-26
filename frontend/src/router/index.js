import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 路由配置
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false // 不需要认证
    }
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: {
      title: '首页',
      requiresAuth: true, // 需要认证
      adminOnly: true
    }
  },
  {
    path: '/patient',
    name: 'PatientIndex',
    component: () => import('@/views/patient/PatientIndex.vue'),
    redirect: () => ({ name: 'PatientList' }),
    meta: {
      title: '病人管理',
      requiresAuth: true
    },
    children: [
      {
        path: 'list',
        name: 'PatientList',
        component: () => import('@/views/patient/PatientList.vue'),
        meta: { title: '病人信息', requiresAuth: true }
      },
      {
        path: 'appointments',
        name: 'AppointmentList',
        component: () => import('@/views/patient/AppointmentList.vue'),
        meta: { title: '挂号预约管理', requiresAuth: true }
      },
      {
        path: 'records',
        name: 'MedicalRecordList',
        component: () => import('@/views/patient/MedicalRecordList.vue'),
        meta: { title: '病历记录管理', requiresAuth: true }
      },
      {
        path: 'appointments/add',
        name: 'AppointmentForm',
        component: () => import('@/views/patient/AppointmentForm.vue'),
        meta: { title: '在线挂号', requiresAuth: true }
      }
    ]
  },
  {
    path: '/patient/detail/:id',
    name: 'PatientDetail',
    component: () => import('@/views/patient/PatientDetail.vue'),
    meta: {
      title: '病人详情',
      requiresAuth: true
    }
  },
  {
    path: '/patient/medical-record/:id',
    name: 'MedicalRecordDetail',
    component: () => import('@/views/patient/MedicalRecordDetail.vue'),
    meta: {
      title: '病历详情',
      requiresAuth: true
    }
  },
  {
    path: '/doctor/medical-records',
    name: 'DoctorMedicalRecordList',
    component: () => import('@/views/doctor/DoctorMedicalRecordList.vue'),
    meta: {
      title: '我的病历',
      requiresAuth: true,
      doctorOnly: true
    }
  },
  {
    path: '/doctor',
    name: 'Doctor',
    component: () => import('@/views/doctor/DoctorList.vue'),
    meta: {
      title: '医生管理',
      requiresAuth: true
    }
  },
  {
    path: '/doctor/dashboard',
    name: 'DoctorDashboard',
    component: () => import('@/views/doctor/DoctorDashboard.vue'),
    meta: {
      title: '医生工作台',
      requiresAuth: true,
      doctorOnly: true
    }
  },
  {
    path: '/doctor/detail/:id',
    name: 'DoctorDetail',
    component: () => import('@/views/doctor/DoctorDetail.vue'),
    meta: {
      title: '医生详情',
      requiresAuth: true
    }
  },
  {
    path: '/doctor/schedule',
    name: 'DoctorSchedule',
    component: () => import('@/views/doctor/DoctorSchedule.vue'),
    meta: {
      title: '医生排班管理',
      requiresAuth: true
    }
  },
  {
    path: '/doctor/leave',
    name: 'DoctorLeave',
    component: () => import('@/views/doctor/DoctorLeave.vue'),
    meta: {
      title: '医生请假管理',
      requiresAuth: true
    }
  },
  {
    path: '/doctor/performance',
    name: 'DoctorPerformance',
    component: () => import('@/views/doctor/DoctorPerformance.vue'),
    meta: {
      title: '医生绩效管理',
      requiresAuth: true
    }
  },
  {
    path: '/doctor/medication-requests',
    name: 'DoctorMedicationRequest',
    component: () => import('@/views/doctor/DoctorMedicationRequest.vue'),
    meta: {
      title: '医生开药申请',
      requiresAuth: true
    }
  },
  {
    path: '/doctor/patients',
    name: 'DoctorPatientList',
    component: () => import('@/views/doctor/DoctorPatientList.vue'),
    meta: {
      title: '我的病人',
      requiresAuth: true,
      doctorOnly: true
    }
  },
  {
    path: '/pharmacy',
    name: 'PharmacyHome',
    component: () => import('@/views/pharmacy/PharmacyIndex.vue'),
    meta: {
      title: '药品管理',
      requiresAuth: true,
      adminOnly: true
    }
  },
  {
    path: '/pharmacy/inventory',
    name: 'PharmacyInventory',
    component: () => import('@/views/pharmacy/PharmacyInventory.vue'),
    meta: {
      title: '库存监控',
      requiresAuth: true,
      adminOnly: true
    }
  },
  {
    path: '/pharmacy/info',
    name: 'PharmacyInfo',
    component: () => import('@/views/pharmacy/PharmacyCatalog.vue'),
    meta: {
      title: '药品信息',
      requiresAuth: true
    }
  },
  {
    path: '/portal',
    name: 'PortalIndex',
    component: () => import('@/views/portal/PortalIndex.vue'),
    meta: {
      title: '病人服务门户',
      requiresAuth: false // Temporarily false for development
    }
  },
  {
    path: '/portal/appointment-booking',
    name: 'PortalAppointmentBooking',
    component: () => import('@/views/portal/AppointmentBooking.vue'),
    meta: {
      title: '在线预约挂号',
      requiresAuth: false // Temporarily false for development
    }
  },
  {
    path: '/portal/family-management',
    name: 'PortalFamilyManagement',
    component: () => import('@/views/portal/FamilyManagement.vue'),
    meta: {
      title: '家庭成员管理',
      requiresAuth: false // Temporarily false for development
    }
  },
  {
    path: '/portal/profile',
    name: 'PortalProfile',
    component: () => import('@/views/portal/ProfileManagement.vue'),
    meta: {
      title: '个人信息管理',
      requiresAuth: true // 需要登录才能访问
    }
  },
  {
    path: '/pharmacy/purchase',
    name: 'PharmacyPurchase',
    component: () => import('@/views/pharmacy/PharmacyPurchase.vue'),
    meta: {
      title: '药品采购管理',
      requiresAuth: true,
      adminOnly: true
    }
  },
  {
    path: '/pharmacy/requests',
    name: 'PharmacyRequests',
    component: () => import('@/views/pharmacy/PharmacyRequests.vue'),
    meta: {
      title: '用药申请审核',
      requiresAuth: true,
      adminOnly: true
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局前置守卫 - 认证检查
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 医院管理系统` : '医院管理系统'
  
  const userStore = useUserStore()
  const requiresAuth = to.meta.requiresAuth !== false // 默认需要认证
  const requiresAdmin = to.meta.adminOnly === true
  const requiresDoctor = to.meta.doctorOnly === true
  
  // 检查是否需要认证
  if (requiresAuth && !userStore.isLoggedIn) {
    // 需要认证但未登录，跳转到登录页
    next({
      path: '/login',
      query: { redirect: to.fullPath } // 保存原始路径，登录后跳转回去
    })
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    // 已登录用户访问登录页，根据角色重定向
    const userRole = userStore.userInfo?.role
    if (userRole === 'user') {
      next({ path: '/portal' })
    } else if (userRole === 'doctor') {
      next({ path: '/doctor/dashboard' })
    } else {
      next({ path: '/' })
    }
  } else if (requiresAdmin && !userStore.isAdmin) {
    // 非管理员访问管理员专属页面，根据角色跳转到各自的主页
    const userRole = userStore.userInfo?.role
    if (userRole === 'doctor') {
      next({ path: '/doctor/dashboard' })
    } else if (userRole === 'user') {
      next({ path: '/portal' })
    } else {
      next({ path: '/login' })
    }
  } else if (requiresDoctor && !userStore.isDoctor) {
    // 非医生访问医生专属页面，根据角色跳转到对应主页
    const userRole = userStore.userInfo?.role
    if (userRole === 'admin') {
      next({ path: '/' })
    } else if (userRole === 'user') {
      next({ path: '/portal' })
    } else {
      next({ path: '/login' })
    }
  } else {
    // 正常访问
    next()
  }
})

// 全局后置钩子 - 页面加载完成
router.afterEach(() => {
  // 可以在这里添加页面加载完成后的逻辑
  // 例如：关闭加载动画等
})

export default router
