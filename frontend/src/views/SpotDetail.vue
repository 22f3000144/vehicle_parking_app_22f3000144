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

          <td>{{ spot.id }}</td>

          <td>
            <span v-if="spot.status === 'O'" class="badge bg-danger">Occupied</span>
            <span v-else class="badge bg-success">Available</span>
          </td>

          <td>
            <div v-if="spot.status === 'O'">
              <div v-if="spot.user">
                Vehicle: {{ spot.user.model }}<br />
                User: {{ spot.user.username }}
              </div>
              <div v-else>
                <em>Info...</em>
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
    const token = localStorage.getItem("token");

    try {
      // Load lot
      const res = await axios.get(
        `http://127.0.0.1:5000/api/lots/${lot_id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      this.lot = res.data;

      // Load spots
      this.spots = res.data.spots.map(s => ({
        ...s,
        user: null // Will fill later
      }));

      // Fetch user data for occupied spots
      for (let spot of this.spots) {
        if (spot.status === "O" && spot.user_id) {
          try {
            const userRes = await axios.get(
              `http://127.0.0.1:5000/api/users/${spot.user_id}`,
              { headers: { Authorization: `Bearer ${token}` } }
            );
            spot.user = userRes.data;
          } catch (e) {
            spot.user = null;
          }
        }
      }

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
