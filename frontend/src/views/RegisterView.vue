<template>
  <div class="container mt-5" style="max-width: 500px;">
    <h3 class="text-center mb-3">Register</h3>
    <div class="card p-4 shadow-sm">
      <form @submit.prevent="registerUser">
        <div class="mb-3">
          <label>Username</label>
          <input v-model="username" class="form-control" type="text" required />
        </div>

        <div class="mb-3">
          <label>Email</label>
          <input v-model="email" class="form-control" type="email" required />
        </div>

        <div class="mb-3">
          <label>Vehicle Model</label>
          <input v-model="model" class="form-control" type="text" placeholder="Optional" />
        </div>

        <div class="mb-3">
          <label>Password</label>
          <input v-model="password" class="form-control" type="password" required />
        </div>

        <button class="btn btn-primary w-100" type="submit">Register</button>
      </form>

      <div class="text-center mt-3">
        <router-link to="/login">Already have an account? Login</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios"
import { useRouter } from "vue-router"
import { ref } from "vue"

const router = useRouter()
const username = ref("")
const email = ref("")
const model = ref("")
const password = ref("")

async function registerUser() {
  try {
    const res = await axios.post("/api/register", {
      username: username.value,
      email: email.value,
      model: model.value,
      password: password.value
    })
    alert(res.data.message || "Registration successful!")
    router.push("/login")
  } catch (err) {
    alert(err.response?.data?.message || "Registration failed")
  }
}
</script>
