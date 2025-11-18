<template>
  <div style="background-color: #f9f9f9; min-height: 100vh;">
    <!-- Navbar -->
    <nav
      class="navbar navbar-expand-lg"
      style="background-color: teal; border-bottom: 2px solid turquoise;"
    >
      <div class="container-fluid">
        <span class="navbar-brand fw-bold" style="color: turquoise;">Admin Panel</span>
        <div class="collapse navbar-collapse">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <RouterLink to="/adminhome" class="nav-link text-white" style="cursor:pointer;">Home</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink to="/userlist" class="nav-link text-white" style="cursor:pointer;">Users</RouterLink>
            </li>
            <li class="nav-item">
              
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Content Section -->
    <div class="container mt-5">
      <div class="card shadow">
        <div class="card-body text-center">
          <h2
            class="mb-4"
            style="color: teal; font-weight: bold; text-shadow: 1px 1px 3px rgba(0,128,128,0.3);"
          >
            Reservation Records
          </h2>

          <img
            :src="chartUrl"
            alt="Reservation Summary Chart"
            class="img-fluid rounded"
            style="max-width: 90%; border: 3px solid turquoise;"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios"

export default {
  name: "AdminSummaryChart",
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
        const res = await axios.get("http://localhost:5000/api/admin/summary", {
          headers: { Authorization: `Bearer ${token}` },
        })
        this.chartUrl = res.data.chart_url1 // Keep backend variable naming intact
      } catch (err) {
        alert(err.response?.data?.message || "Failed to load admin summary chart.")
      }
    },
  },
}
</script>

<style scoped>
.nav-link:hover {
  text-decoration: underline;
}

.card {
  border-radius: 10px;
}

@media (max-width: 768px) {
  .card {
    margin: 1rem;
  }

  h2 {
    font-size: 1.2rem;
  }

  img {
    max-width: 100%;
  }
}
</style>
