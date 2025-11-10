<template>
  <div class="container mt-5" style="max-width: 450px;">
    <h3 class="mb-3 text-center">Login</h3>
    <div class="card p-4 shadow-sm">
      <form @submit.prevent="loginUser">
        <div class="mb-3">
          <label>Email</label>
          <input type="email" v-model="email" class="form-control" required />
        </div>
        <div class="mb-3">
          <label>Password</label>
          <input type="password" v-model="password" class="form-control" required />
        </div>
        <button type="submit" class="btn btn-dark w-100">Login</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import axios from "axios"
import { useRouter } from "vue-router"
import { ref } from "vue"

const router = useRouter()
const email = ref("")
const password = ref("")

async function loginUser() {
  try {
    const res = await axios.post("/api/login", {
      email: email.value,
      password: password.value
    })

    const token = res.data.user_details.auth_token
    const roles = res.data.user_details.roles || []

    localStorage.setItem("token", token)
    localStorage.setItem("role", roles.includes("admin") ? "admin" : "user")

    alert("Login successful")

    if (roles.includes("admin")) {
      router.push("/admin")
    } else {
      router.push("/user")
    }
  } catch (err) {
    alert(err.response?.data?.message || "Login failed")
  }
}
</script>
