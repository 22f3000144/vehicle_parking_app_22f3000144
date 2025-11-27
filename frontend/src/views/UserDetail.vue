<template>
  <div class="p-4 bg-light" id="user-detail-body">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-4 mb-4">
      <div class="navbar-nav w-100 d-flex justify-content-between align-items-center">
        <div>
          <a class="navbar-brand fw-bold">Admin Panel</a>
          <router-link to="/adminhome" class="nav-link d-inline text-white">Home</router-link>
          <router-link to="/adminchart" class="nav-link d-inline text-white">Summary</router-link>
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
             
            </tr>
          </thead>
          <tbody class="text-center">
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.id }}</td>
              <td>{{ user.username }}</td>
              <td>{{ user.email }}</td>
              <td>{{ user.model || '-' }}</td>
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

<script>
import axios from "axios";

export default {
  data() {
    return {
      users: []
    };
  },
  methods: {
    async fetchUsers() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://127.0.0.1:5000/api/users", {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.users = res.data;
      } catch (err) {
        console.log("wtf.. try agingyoou can do it..");
      }
    },
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      this.$router.push("/login");
    }
  },
  mounted() {
    this.fetchUsers();
  }
};
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
