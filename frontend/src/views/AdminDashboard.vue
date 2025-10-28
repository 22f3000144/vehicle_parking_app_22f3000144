<template>
  <div class="container mt-4">
    <h3>Welcome, Admin!</h3>
    <p>You can manage parking lots, users, and view reports.</p>
    <button @click="logout" class="btn btn-danger mt-3">Logout</button>
    <button @click="addparkinglot" > + Add Parking </button>


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
