import { createRouter, createWebHistory } from 'vue-router'

// Views
import HomeView from '../views/HomeView.vue'
import ResisterView from '../views/ResisterView.vue'
import LoginView from '../views/LoginView.vue'
import UserDashboard from '../views/UserDashboard.vue'
import AdminDashboard from '../views/AdminDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue'),
  },
  {
    path: '/resisteration',
    name: 'register',
    component: () => import('../views/ResisterView.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/user',
    name: 'user_dashboard',
    component: UserDashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'admin_dashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// ✅ Navigation Guards
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (to.meta.requiresAuth && !token) {
    // Protected route but no token → redirect to login
    next({ name: 'login' })
  } else if (to.name === 'login' && token) {
    // If logged in already → redirect based on role
    if (role === 'admin') next({ name: 'admin_dashboard' })
    else next({ name: 'user_dashboard' })
  } else {
    next()
  }
})

export default router
