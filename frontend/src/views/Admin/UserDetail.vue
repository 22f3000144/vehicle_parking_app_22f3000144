<template>
  <div class="p-4 bg-light" id="user-detail-body">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-4 mb-4">
      <div class="navbar-nav w-100 d-flex justify-content-between align-items-center">
        <div>
          <a class="navbar-brand fw-bold">Admin Panel</a>
          <router-link to="/admin" class="nav-link d-inline text-white">Home</router-link>
          <router-link to="/admin-summary" class="nav-link d-inline text-white">Summary</router-link>
        </div>
        <button @click="logout" class="btn btn-outline-light btn-sm">Log-out</button>
      </div>
    </nav>

    <!-- Users Table -->
    <div class="container bg-white shadow-sm p-4 rounded">
      <h3 class="mb-3 text-dark text-center">User List</h3>

      <div class="table-responsive">
        <table class="table table-striped table-bordered align-middle">
          <thead class="table-dark text-center">
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Email</th>
              <th>Model</th>
              <th>Role</th>
            </tr>
          </thead>
          <tbody class="text-center">
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.model || '-' }}</td>
              <td>
                <span
                  :class="user.roles.includes('admin') ? 'badge bg-danger' : 'badge bg-secondary'"
                >
                  {{ user.roles.join(', ') }}
                </span>
              </td>
            </tr>

            <tr v-if="!users.length">
              <td colspan="5" class="text-muted text-center">No users found.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from "axios"
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const users = ref([])

// ✅ Fetch all users (admin only)
async function fetchUsers() {
  try {
    const token = localStorage.getItem("token")
    const res = await axios.get("/api/users", {
      headers: { Authorization: `Bearer ${token}` },
    })
    users.value = res.data
  } catch (err) {
    alert(err.response?.data?.message || "Failed to load user list.")
  }
}

// ✅ Logout handler
function logout() {
  localStorage.removeItem("token")
  localStorage.removeItem("role")
  router.push("/login")
}

onMounted(fetchUsers)
</script>

<style scoped>
#user-detail-body {
  min-height: 100vh;
}
.nav-link {
  cursor: pointer;
}
.table {
  font-size: 0.95rem;
}
</style>
