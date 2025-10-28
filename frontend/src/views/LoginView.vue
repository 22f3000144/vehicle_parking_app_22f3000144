<script setup>
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const password = ref('')

async function login() {
  try {
    const res = await axios.post('http://127.0.0.1:5000/api/login', {
      email: email.value,
      password: password.value
    })
    const { token, role } = res.data

    localStorage.setItem('token', token)
    localStorage.setItem('role', role)

    if (role === 'admin') router.push('/admin')
    else router.push('/user')
  } catch (err) {
    alert(err.response?.data?.message || 'Login failed')
  }
}
</script>



<template>
  <div class="container mt-5 col-md-4">
    <h3 class="text-center mb-4">Login</h3>
    <div class="card p-4 shadow-sm">
      <div class="mb-3">
        <label>Email</label>
        <input v-model="email" type="email" class="form-control" placeholder="Enter your email" />
      </div>
      <div class="mb-3">
        <label>Password</label>
        <input v-model="password" type="password" class="form-control" placeholder="Enter your password" />
      </div>
      <button @click="login" class="btn btn-primary w-100">Login</button>
      <p class="text-center mt-3">
        Don’t have an account? <router-link to="/register">Register</router-link>
      </p>
    </div>
  </div>
</template>

