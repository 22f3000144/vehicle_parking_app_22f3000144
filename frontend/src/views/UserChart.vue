<template>
  <div
    style="
      margin: 0;
      padding: 0;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background-size: cover;
      background-repeat: no-repeat;
      background-position: center;
      color: white;
      min-height: 100vh;
    "
  >
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg" style="background-color: rgba(0, 128, 128, 0.9); padding: 10px 20px;">
      <div class="container-fluid">
        <RouterLink to="/user" class="navbar-brand fw-bold text-white">🏠 Home</RouterLink>
        <div class="navbar-nav">
          <RouterLink to="/reservation" class="nav-link text-white">Book Parking</RouterLink>
          <RouterLink to="/logout" class="nav-link text-white">Log-out</RouterLink>
        </div>
      </div>
    </nav>

    <!-- Summary Card -->
    <div class="container mt-5" style="max-width: 900px;">
      <div
        class="card shadow rounded-3"
        style="background-color: rgba(0, 0, 0, 0.8); border: 2px solid turquoise;"
      >
        <div class="card-body">
          <h2 class="card-title text-center mb-4" style="color: turquoise;">
            Your Parking Cost Summary
          </h2>

          <div class="text-center">
            <img
              :src="chartUrl"
              alt="Parking Cost Summary Chart"
              class="img-fluid rounded border"
              style="max-width: 90%; border: 2px solid teal;"
            />
          </div>

          <div class="mt-4 text-center">
            <!-- Optional extra actions -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios"

export default {
  name: "UserSummaryChart",
  data() {
    return {
      chartUrl: "",
    }
  },
  async mounted() {
    await this.fetchChart()
  },
  methods: {
    async fetchChart() {
      try {
        const token = localStorage.getItem("token")
        const res = await axios.get("http://localhost:5000/api/user/summary-chart", {
          headers: { Authorization: `Bearer ${token}` },
        })
        this.chartUrl = res.data.chart_url2 // adjust key name to match your backend response
      } catch (err) {
        alert(err.response?.data?.message || "Failed to load summary chart.")
      }
    },
  },
}
</script>

<style scoped>
.nav-link:hover {
  text-decoration: underline;
}

@media (max-width: 768px) {
  .card {
    margin: 10px;
  }

  .card-title {
    font-size: 1.2rem;
  }

  img {
    max-width: 100%;
  }
}
</style>
