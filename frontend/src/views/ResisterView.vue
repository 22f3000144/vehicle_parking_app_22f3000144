<template>
  <div class="container mt-5 col-md-4">
    <h3 class="text-center mb-4">Register</h3>
    <div class="card p-4 shadow-sm">
      <div class="mb-3">
        <label>Username</label>
        <input v-model="username" type="text" class="form-control" />
      </div>
      <div class="mb-3">
        <label>Email</label>
        <input v-model="email" type="email" class="form-control" />
      </div>
      <div class="mb-3">
        <label>Car Model</label>
        <input v-model="model" type="text" class="form-control" />
      </div>
      <div class="mb-3">
        <label>Password</label>
        <input v-model="password" type="password" class="form-control" />
      </div>
      <button @click="register" class="btn btn-success w-100">Register</button>
      <p class="text-center mt-3">
        Already have an account? <router-link to="/login">Login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const email = ref('')
const model = ref('')
const password = ref('')

async function register() {
  try {
    await axios.post('http://127.0.0.1:5000/register', {
      username: username.value,
      email: email.value,
      model: model.value,
      password: password.value
    })
    alert('Registration successful! You can now log in.')
    router.push('/')
  } catch (err) {
    alert(err.response?.data?.message || 'Registration failed')
  }
}
</script>
