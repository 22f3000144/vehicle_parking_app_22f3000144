<template>
  <div class="container mt-4">

    <!-- NAVBAR -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-4 mb-4">
      <div class="container-fluid">
        <a class="navbar-brand fw-bold text-white">User Portal</a>
        <div class="navbar-nav ms-auto">
          <RouterLink to="/userhome" class="nav-link text-white">🏠 Home</RouterLink>
          <RouterLink to="/userchart" class="nav-link text-white">Summary</RouterLink>
          <RouterLink to="/reserve" class="nav-link text-white">Book Parking</RouterLink>
          <a @click="logout" class="nav-link text-white" style="cursor:pointer;">Log-out</a>
          <button class="btn btn-success" @click="exportHistory">
            Export Parking History
          </button> 
          <button class="btn btn-primary ms-2"
                  @click="checkExportStatus"
                  :disabled="!taskId">
            Check Export Status
          </button>
        </div>
      </div>
    </nav>

    <!-- PAGE TITLE -->
    <h1 class="text-center mb-4">Welcome to Your Dashboard</h1>

    <!-- HISTORY TABLE -->
    <h3 class="mb-3 text-dark">Your Parking History</h3>

    <div class="table-responsive">
      <table class="table table-bordered table-hover align-middle bg-white shadow-sm">
        <thead class="table-dark text-center">
          <tr>
            <th>Reservation ID</th>
            <th>Lot Location</th>
            <th>Parked At</th>
            <th>Left At</th>
            <th>Cost (₹)</th>
            <th>Action</th>
          </tr>
        </thead>

        <tbody class="text-center">
          <tr v-for="res in reservations" :key="res.id">

            <td>{{ res.id }}</td>

            <!-- LOT NAME -->
            <td>{{ res.lot_name || 'Unknown' }}</td>

            <!-- START TIME -->
            <td>
              {{ formatDate(res.parking_timestamp) || 'Not Started' }}
            </td>

            <!-- END TIME -->
            <td>
              {{ formatDate(res.leaving_timestamp) || 'In Progress' }}
            </td>

            <!-- COST -->
            <td>
              {{ res.parking_cost !== null ? res.parking_cost : '-' }}
            </td>

            <!-- ACTIONS -->
            <td>
              <button
                v-if="!res.parking_timestamp"
                class="btn btn-primary btn-sm"
                @click="startParking(res.spot_id)"
              >
                🚗 In
              </button>

              <button
                v-else-if="res.parking_timestamp && !res.leaving_timestamp"
                class="btn btn-warning btn-sm"
                @click="releaseParking(res.id)"
              >
                🏁 Release
              </button>

              <button
                v-else
                class="btn btn-secondary btn-sm"
                disabled
              >
                ✅ Completed
              </button>
            </td>

          </tr>

          <tr v-if="reservations.length === 0">
            <td colspan="6" class="text-muted">No reservations yet.</td>
          </tr>

        </tbody>

      </table>
    </div>

  </div>
</template>

<script>
import axios from "axios"

export default {
  name: "UserHistory",

  data() {
    return {
      reservations: [], 
      taskId: null
    }
  },

  mounted() {
    this.fetchHistory()
  },

  methods: {
    async fetchHistory() {
      try {
        const token = localStorage.getItem("token")

        const res = await axios.get("http://127.0.0.1:5000/api/reservations", {
          headers: { Authorization: `Bearer ${token}` }
        })

        // Attach lot name for each reservation
        // (Need an extra fetch for spot → lot)
        await this.attachLotNames(res.data)
      } catch (err) {
        console.error("Error loading history")
      }
    },
    async checkExportStatus() {
      if (!this.taskId) {
        alert("Start export first.");
        return;
      }

      try {
        const token = localStorage.getItem("token");

        const res = await fetch(
          `http://127.0.0.1:5000/api/export/status?task_id=${this.taskId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        const data = await res.json();
        alert(`Status: ${data.status}`);
      } catch (err) {
        alert("Something went wrong while checking status.");
      }
    },
        async exportHistory() {
        const token = localStorage.getItem("token");

        const res = await fetch("http://localhost:5000/api/export/history", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          }
        });

        const data = await res.json();
        this.exportTaskId = data.task_id;
        alert("Export started. You can check the status.");
      },

    async attachLotNames(history) {
      const token = localStorage.getItem("token")

      for (let r of history) {
        if (!r.spot_id) continue

        const spot = await axios.get(`http://127.0.0.1:5000/api/spots/${r.spot_id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })

        const lot = await axios.get(`http://127.0.0.1:5000/api/lots/${spot.data.lot_id}`, {
          headers: { Authorization: `Bearer ${token}` }
        })

        r.lot_name = lot.data.prime_location_name
      }

      this.reservations = history
    },

    // Start parking
    async startParking(spotId) {
      try {
        const token = localStorage.getItem("token")

        await axios.post(
          "http://127.0.0.1:5000/api/reserve",
          { spot_id: spotId },
          { headers: { Authorization: `Bearer ${token}` } }
        )

        this.fetchHistory()
      } catch (err) {
        alert(err.response?.data?.message || "Error starting parking")
      }
    },

    // Release parking
    async releaseParking(reservationId) {
      try {
        const token = localStorage.getItem("token");

        const res = await axios.post(
          "http://127.0.0.1:5000/api/release",
          { reservation_id: reservationId },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        alert(`
          🏁 Parking Released!
          Duration: ${res.data.duration_minutes} minutes
          Cost: ₹${res.data.cost}
        `);

        this.fetchHistory();

      } catch (err) {
        alert(err.response?.data?.message || "Error releasing parking");
      }
    },

    formatDate(value) {
      if (!value) return null
      return new Date(value).toLocaleString()
    },

    logout() {
      localStorage.clear()
      this.$router.push("/")
    }
  }
}
</script>

<style scoped>
.table {
  font-size: 0.9rem;
}
@media (max-width: 768px) {
  .table {
    font-size: 0.8rem;
  }
}
</style>
