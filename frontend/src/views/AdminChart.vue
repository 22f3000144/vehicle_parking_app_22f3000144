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
              <RouterLink to="/adminhome" class="nav-link text-white">Home</RouterLink>
            </li>
            <li class="nav-item">
              <RouterLink to="/userlist" class="nav-link text-white">Users</RouterLink>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Chart Section -->
    <div class="container mt-5">
      <div class="card shadow">
        <div class="card-body">
          <h2 class="mb-4 text-center" style="color: teal; font-weight: bold;">
            Parking Lot Usage Summary
          </h2>

          <div class="text-center mb-3">
            <canvas id="adminChart" style="max-width: 90%;"></canvas>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { Chart, registerables } from "chart.js";

Chart.register(...registerables);

export default {
  name: "AdminSummaryChart",
  data() {
    return {
      lotUsage: [],
      totalSpots: 0,
      occupiedSpots: 0,
      availableSpots: 0,
    };
  },

  async mounted() {
    await this.fetchChartData();
  },

  methods: {
    async fetchChartData() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://localhost:5000/api/admin/summary", {
          headers: { Authorization: `Bearer ${token}` },
        });

        this.lotUsage = res.data.lot_usage;
        this.totalSpots = res.data.total_spots;
        this.occupiedSpots = res.data.occupied_spots;
        this.availableSpots = res.data.available_spots;

        this.renderChart();
      } catch (err) {
        alert(err.response?.data?.message || "Failed to load admin summary chart.");
      }
    },

    renderChart() {
      if (!this.lotUsage || this.lotUsage.length === 0) return;

      const ctx = document.getElementById("adminChart").getContext("2d");

      new Chart(ctx, {
        type: "bar",
        data: {
          labels: this.lotUsage.map((l) => l.lot_name),
          datasets: [
            {
              label: "Occupied Spots",
              data: this.lotUsage.map((l) => l.used),
              backgroundColor: "teal",
            },
            {
              label: "Available Spots",
              data: this.lotUsage.map((l) => l.total - l.used),
              backgroundColor: "lightgreen",
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" },
            title: {
              display: true,
              text: "Parking Lot Occupancy",
              font: { size: 18 },
              color: "teal",
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { color: "#333" },
            },
            x: {
              ticks: { color: "#333" },
            },
          },
        },
      });
    },
  },
};
</script>

<style scoped>
.nav-link:hover {
  text-decoration: underline;
}

.card {
  border-radius: 12px;
}

@media (max-width: 768px) {
  .card {
    margin: 1rem;
  }

  h2 {
    font-size: 1.2rem;
  }

  canvas {
    max-width: 100%;
  }
}
</style>
