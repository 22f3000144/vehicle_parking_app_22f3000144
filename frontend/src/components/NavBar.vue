<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light shadow-sm">
    <div class="container-fluid">
      <a class="navbar-brand fw-bold" href="#">ParkSafe</a>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#mainNavbar"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="mainNavbar">
        <ul class="navbar-nav ms-auto mb-2 mb-lg-0">

          <!-- Public Links -->
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link class="nav-link" :to="{ name: 'home' }">Home</router-link>
          </li>
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link class="nav-link" :to="{ name: 'login' }">Login</router-link>
          </li>
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link class="nav-link" :to="{ name: 'register' }">Register</router-link>
          </li>

          <!-- User Links -->
          <li class="nav-item" v-if="isLoggedIn && role === 'user'">
            <router-link class="nav-link" :to="{ name: 'user_dashboard' }">Dashboard</router-link>
          </li>
          <li class="nav-item" v-if="isLoggedIn && role === 'user'">
            <router-link class="nav-link" :to="{ name: 'Reserve' }">Reserve Parking</router-link>
          </li>

          <!-- Admin Links -->
          <li class="nav-item" v-if="isLoggedIn && role === 'admin'">
            <router-link class="nav-link" :to="{ name: 'admin_dashboard' }">Admin Panel</router-link>
          </li>

          <li class="nav-item" v-if="isLoggedIn && role === 'admin'">
            <router-link class="nav-link" :to="{ name: 'user_list' }">Users</router-link>
          </li>

          <li class="nav-item" v-if="isLoggedIn && role === 'admin'">
            <router-link class="nav-link" :to="{ name: 'AddParking' }">Add Lot</router-link>
          </li>

          <!-- Logout -->
          <li class="nav-item" v-if="isLoggedIn">
            <button class="btn btn-sm btn-outline-danger ms-2" @click="logout">
              Logout
            </button>
          </li>

        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: "Navbar",
  data() {
    return {
      isLoggedIn: false,
      role: null,
    };
  },
  mounted() {
    const token = localStorage.getItem("token");
    const userRole = localStorage.getItem("role");

    if (token) {
      this.isLoggedIn = true;
      this.role = userRole;
    }
  },
  methods: {
    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("role");
      this.isLoggedIn = false;
      this.role = null;
      this.$router.push({ name: "login" });
    },
  },
};
</script>

<style scoped>
.navbar-brand {
  font-size: 1.4rem;
}
</style>
