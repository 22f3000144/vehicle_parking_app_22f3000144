import { createRouter, createWebHistory } from 'vue-router'

// Views

import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue'
import LoginView from '../views/LoginView.vue'

// User Components
import UserDashboard from '../views/User/UserDashboard.vue'


// admin components
import AdminDashboard from '../views/Admin/AdminDashboard.vue'
import UserDetail from '../views/Admin/UserDetail.vue'
import AddParkingLot from '../views/Admin/AddParkingLot.vue'
import EditParkingLot from '../views/Admin/EditParkingLot.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/about', name: 'about', component: AboutView },
  { path: '/registration', name: 'register', component: RegisterView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/userlist', name: 'user_list', 
    component: UserDetail, 
    meta: { requiresAuth: true } 
  },
  { path: '/add-parking-lot', name: 'add_lot', 
    component: AddParkingLot,
     meta: { requiresAuth: true } 
  },
  { path: '/edit-lot/:id', name: 'edit_lot', 
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
