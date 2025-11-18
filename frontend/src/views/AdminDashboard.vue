<template>
  <div class="p-4 bg-light" id="admin-body">

    <!-- NAVBAR -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark px-4 mb-4" id="admin-nav">
      <div class="navbar-nav w-100 d-flex justify-content-between align-items-center">
        <div>
          <a class="navbar-brand fw-bold">Admin Panel</a>

          <!-- Corrected Paths -->
          <router-link to="/adminhome" class="nav-link d-inline text-white">Home</router-link>
          <router-link to="/userlist" class="nav-link d-inline text-white">Users</router-link>
          <router-link to="/adminchart" class="nav-link d-inline text-white">Summary</router-link>
        </div>

        <button @click="logout" class="btn btn-outline-light btn-sm">Logout</button>
      </div>
    </nav>


    <!-- Parking Lot Section -->
    <div class="container" id="admin-table-container">

      <div class="d-flex justify-content-between align-items-center mb-3">
        <h3 class="text-dark">Parking Lots</h3>

        
        <router-link to="/addparking" class="btn btn-success btn-sm">
          + Add Parking Lot
        </router-link>
      </div>


      <!-- Loading Spinner -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>


      <!-- Parking Lots Table -->
      <table
        v-else
        class="table table-bordered table-striped table-hover bg-white shadow-sm"
        id="parking-lot-table"
      >
        <thead class="table-dark">
          <tr>
            <th>ID</th>
            <th>Location</th>
            <th>Price</th>
            <th>Address</th>
            <th>Pin Code</th>
            <th>Max Spots</th>
            <th>Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="lot in parkingLots" :key="lot.id">
            <td>{{ lot.id }}</td>
            <td>{{ lot.prime_location_name }}</td>
            <td>{{ lot.price }}</td>
            <td>{{ lot.address }}</td>
            <td>{{ lot.pin_code }}</td>
            <td>{{ lot.max_spot }}</td>

            <td>
              <!-- Corrected Spot Detail Path -->
              <router-link
                :to="`/spotdetail/${lot.id}`"
                class="btn btn-sm btn-secondary me-1"
              >
                Detail
              </router-link>

              <!-- Corrected Edit Path -->
              <router-link
                :to="`/editlot/${lot.id}`"
                class="btn btn-sm btn-warning me-1"
              >
                Edit
              </router-link>

              <button @click="deleteLot(lot.id)" class="btn btn-sm btn-danger">
                Delete
              </button>
            </td>
          </tr>

          <tr v-if="!parkingLots.length">
            <td colspan="7" class="text-center text-muted">No parking lots available.</td>
          </tr>
        </tbody>
      </table>

    </div>
  </div>
</template>



<script>
import axios from "axios";

export default {
  data() {
    return {
      parkingLots: [],
      loading: true
    };
  },

  methods: {
    async fetchParkingLots() {
      try {
        const token = localStorage.getItem("token");

        const res = await axios.get("http://127.0.0.1:5000/api/lots", {
          headers: { Authorization: `Bearer ${token}` }
        });

        this.parkingLots = res.data;

      } catch (err) {
        alert(err.response?.data?.message || "Failed to load parking lots");
      } finally {
        this.loading = false;
      }
    },

    async deleteLot(lotId) {
      if (!confirm("Are you sure you want to delete this lot?")) return;

      try {
        const token = localStorage.getItem("token");

        const res = await axios.delete(`http://127.0.0.1:5000/api/lots/${lotId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (res.status === 200) {
          this.parkingLots = this.parkingLots.filter((lot) => lot.id !== lotId);
          alert("Parking lot deleted successfully.");
        }

      } catch (err) {
        alert(err.response?.data?.message || "Failed to delete lot. Ensure lot is empty.");
      }
    },

    logout() {
      localStorage.removeItem("token");
      localStorage.removeItem("role");

      this.$router.push({ name: "adminlogin" });
    }
  },

  mounted() {
    // Prevent normal users from entering admin area
    if (localStorage.getItem("role") !== "admin") {
      this.$router.push({ name: "userhome" });
      return;
    }

    // Load parking lots
    this.fetchParkingLots();
  }
};
</script>



<style scoped>
#admin-body {
  min-height: 100vh;
}

.nav-link {
  cursor: pointer;
}

.table {
  font-size: 0.9rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  #admin-body {
    padding: 1rem;
  }

  .table {
    font-size: 0.85rem;
  }

  nav .navbar-brand {
    font-size: 1rem;
  }

  .btn {
    font-size: 0.8rem;
  }
}
</style>
