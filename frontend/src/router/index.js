import { createRouter, createWebHistory } from 'vue-router'

// Views
import HomeView from '../views/HomeView.vue'
import RegisterView from '../views/RegisterView.vue'

// User Components
import UserDashboard from '../views/UserDashboard.vue'
import ReserveParking from '../views/ReserveParking.vue'
import UserChart from '../views/UserChart.vue'
import UserLogin from '../views/UserLogin.vue'

// Admin Components
import AdminDashboard from '../views/AdminDashboard.vue'
import UserDetail from '../views/UserDetail.vue'
import AddParkingLot from '../views/AddParkingLot.vue'
import EditParkingLot from '../views/EditParkingLot.vue'
import AdminChart from '../views/AdminChart.vue'
import AdminLogin from '../views/AdminLogin.vue'
import SpotDetail from '../views/SpotDetail.vue'   


const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/userlogin', name: 'userlogin', component: UserLogin },
  { path: '/adminlogin', name: 'adminlogin', component: AdminLogin },
  { 
    path: '/userlist', 
    name: 'userlist', 
    component: UserDetail, 
    meta: { requiresAuth: true } 
  },
  { 
    path: '/addparking', 
    name: 'addparking', 
    component: AddParkingLot,
    meta: { requiresAuth: true } 
  },
  { 
    path: '/adminchart', 
    name: 'adminchart', 
    component: AdminChart,
    meta: { requiresAuth: true } 
  },
  { 
    path: '/spotdetail/:id', 
    name: 'spotdetail', 
    component: SpotDetail,
    meta: { requiresAuth: true } 
  },
  { 
    path: '/reserve', 
    name: 'reserve', 
    component: ReserveParking,
    meta: { requiresAuth: true } 
  },
  { 
    path: '/userchart', 
    name: 'userchart', 
    component: UserChart,
    meta: { requiresAuth: true } 
  },
  { 
    path: '/editlot/:id', 
    name: 'editlot', 
    component: EditParkingLot, 
    meta: { requiresAuth: true } 
  },
  {
    path: '/userhome',
    name: 'userhome',
    component: UserDashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/adminhome',
    name: 'adminhome',
    component: AdminDashboard,
    meta: { requiresAuth: true },
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]



const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})


// --------------------------------------------------------------
// ✅ Navigation Guards
// --------------------------------------------------------------

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token")
  const role = localStorage.getItem("role")

  // If route requires auth and user has no token → redirect
  if (to.meta.requiresAuth && !token) {
    if (to.name.includes("admin")) {
      return next({ name: "adminlogin" })
    } else {
      return next({ name: "userlogin" })
    }
  }

  // If logged-in user tries to visit login pages → redirect them
  if ((to.name === "userlogin" || to.name === "adminlogin") && token) {
    if (role === "admin") return next({ name: "adminhome" })
    else return next({ name: "userhome" })
  }

  next()
})


export default router
