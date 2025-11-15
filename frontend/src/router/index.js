import { createRouter, createWebHistory } from 'vue-router'

// Views

import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'

// User Components
import UserDashboard from '../views/UserDashboard.vue'
import ReserveParking from '../views/ReserveParking.vue'

// admin components
import AdminDashboard from '../views/AdminDashboard.vue'
import UserDetail from '../views/UserDetail.vue'
import AddParkingLot from '../views/AddParkingLot.vue'
import EditParkingLot from '../views/EditParkingLot.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/registration', name: 'register', component: RegisterView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/userlist', name: 'user_list', 
    component: UserDetail, 
    meta: { requiresAuth: true } 
  },
  { path: '/AddParking', name: 'AddParking', 
    component: AddParkingLot,
     meta: { requiresAuth: true } 
  },
  { path: '/Reserve', name: 'Reserve', 
    component: ReserveParking,
     meta: { requiresAuth: true } 
  },
  { path: '/edit_lot/:id', name: 'edit_lot', 
    component: EditParkingLot, 
    meta: { requiresAuth: true } 
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
  { path: '/:pathMatch(.*)*', redirect: '/' },
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
    next({ name: 'login' })
  } else if (to.name === 'login' && token) {
    if (role === 'admin') next({ name: 'admin_dashboard' })
    else next({ name: 'user_dashboard' })
  } else {
    next()
  }
})

export default router
