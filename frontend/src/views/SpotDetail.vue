<template>
  <div class="container py-4">

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg mb-4" style="background-color: orange;">
      <div class="container-fluid">
        <a class="navbar-brand fw-bold text-dark">Admin Panel</a>

        <div class="collapse navbar-collapse">
          <ul class="navbar-nav ms-auto">
            <li class="nav-item">
              <router-link to="/adminhome" class="nav-link text-white">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/userlist" class="nav-link text-white">Users</router-link>
            </li>
            <li class="nav-item">
              <router-link to="/adminchart" class="nav-link text-white">Summary</router-link>
            </li>

          </ul>
        </div>
      </div>
    </nav>

    <!-- Title -->
    <h2 class="mb-4">
      Parking Spots in {{ lot.prime_location_name }}
    </h2>

    <!-- Table -->
    <table class="table table-bordered table-striped">
      <thead class="table-dark">
        <tr>
          <th>Spot ID</th>
          <th>Status</th>
          <th>Vehicle Details</th>
        </tr>
      </thead>

      <tbody>
        <tr v-for="spot in spots" :key="spot.id">

          <!-- Spot ID -->
          <td>{{ spot.id }}</td>

          <!-- Status -->
          <td>
            <span v-if="spot.status === 'O'" class="badge bg-danger">Occupied</span>
            <span v-else class="badge bg-success">Available</span>
          </td>

          <!-- Vehicle Details -->
          <td>
            <div v-if="spot.status === 'O'">
              <div v-if="spot.active_reservations.length > 0">
                <div v-for="r in spot.active_reservations" :key="r.id">
                  Vehicle: {{ r.user.model }}<br />
                  User: {{ r.user.username }}<br />
                </div>
              </div>
              <div v-else>
                <em>No vehicle details yet</em>
              </div>
            </div>

            <em v-else>No vehicle parked</em>
          </td>

        </tr>
      </tbody>
    </table>

  </div>
</template>


<script>
import axios from "axios";

export default {
  data() {
    return {
      lot: {},
      spots: []
    };
  },

  async mounted() {
    const lot_id = this.$route.params.id;

    try {
      const res = await axios.get(`http://127.0.0.1:5000/api/lots/${lot_id}`);

      // API returns lot + spots
      this.lot = res.data;
      this.spots = res.data.spots.map(spot => ({
        ...spot,
        active_reservations: spot.reservations?.filter(r => r.leaving_timestamp === null) || []
      }));
      
    } catch (err) {
      alert("Failed to load parking spot details");
    }
  }
};
</script>

<style>
body {
  background-color: white;
  color: black;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}
</style>
