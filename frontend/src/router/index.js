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
      requiresAuth: true // 需要认证
    }
  },
  {
    path: '/patient',
    name: 'Patient',
    component: () => import('@/views/patient/PatientList.vue'),
    meta: {
      title: '病人管理',
      requiresAuth: true
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
    path: '/pharmacy',
    name: 'Pharmacy',
    component: () => import('@/views/pharmacy/PharmacyIndex.vue'),
    meta: {
      title: '药房管理',
      requiresAuth: true
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
  
  // 检查是否需要认证
  if (requiresAuth && !userStore.isLoggedIn) {
    // 需要认证但未登录，跳转到登录页
    next({
      path: '/login',
      query: { redirect: to.fullPath } // 保存原始路径，登录后跳转回去
    })
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    // 已登录用户访问登录页，重定向到首页
    next({ path: '/' })
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
