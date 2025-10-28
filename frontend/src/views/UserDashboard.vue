<template>
  <div class="container mt-4">
    <h3>Welcome, User!</h3>
    <p>This is your parking dashboard.</p>
    <button @click="logout" class="btn btn-danger mt-3">Logout</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

function logout() {
  localStorage.clear()
  router.push('/')
}
</script>
