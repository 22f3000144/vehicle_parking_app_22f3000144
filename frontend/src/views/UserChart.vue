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
        <RouterLink to="/userhome" class="navbar-brand fw-bold text-white">🏠 Home</RouterLink>
        <div class="navbar-nav">
          <RouterLink to="/reserve" class="nav-link text-white">Book Parking</RouterLink>
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
            Your Parking Summary
          </h2>

          <div class="text-center mb-4">
            <canvas id="userChart" style="max-width: 90%;"></canvas>
          </div>

          <div class="mt-4 text-center" v-if="activeReservation">
            <p style="color: lightgreen; font-weight: bold;">
              Active Reservation: Spot #{{ activeReservation.spot_id }} started at {{ new Date(activeReservation.parking_timestamp).toLocaleString() }}
            </p>
          </div>

          <div class="mt-2 text-center">
            <p style="color: turquoise;">Total Reservations: {{ totalReservations }}</p>
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
  name: "UserSummaryChart",
  data() {
    return {
      totalReservations: 0,
      activeReservation: null,
      monthlyUsage: [],
    };
  },
  async mounted() {
    await this.fetchChartData();
  },
  methods: {
    async fetchChartData() {
      try {
        const token = localStorage.getItem("token");
        const res = await axios.get("http://localhost:5000/api/user/summary", {
          headers: { Authorization: `Bearer ${token}` },
        });

        this.totalReservations = res.data.total_reservations;
        this.activeReservation = res.data.active_reservation;
        this.monthlyUsage = res.data.monthly_usage;

        this.renderChart();
      } catch (err) {
        alert(err.response?.data?.message || "Failed to load summary chart.");
      }
    },
    renderChart() {
      if (!this.monthlyUsage || this.monthlyUsage.length === 0) return;

      const ctx = document.getElementById("userChart").getContext("2d");

      new Chart(ctx, {
        type: "bar",
        data: {
          labels: this.monthlyUsage.map((m) => m.month),
          datasets: [
            {
              label: "Reservations",
              data: this.monthlyUsage.map((m) => m.count),
              backgroundColor: "teal",
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: { display: false },
            title: {
              display: true,
              text: "Monthly Parking Usage",
              color: "turquoise",
              font: { size: 16 },
            },
          },
          scales: {
            y: {
              beginAtZero: true,
              title: { display: true, text: "Number of Reservations", color: "white" },
              ticks: { color: "white" },
            },
            x: {
              title: { display: true, text: "Month", color: "white" },
              ticks: { color: "white" },
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

@media (max-width: 768px) {
  .card {
    margin: 10px;
  }

  .card-title {
    font-size: 1.2rem;
  }

  canvas {
    max-width: 100%;
  }
}
</style>
