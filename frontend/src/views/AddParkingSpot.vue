<template>
  <div>

    <!-- Simple Navbar -->
    <nav class="p-3 bg-dark">
      <router-link to="/" class="text-white text-decoration-none">Home</router-link>
    </nav>

    <!-- Form Section -->
    <form @submit.prevent="addSpot" class="container mt-4" style="max-width: 600px;">
      <h3 class="mb-3">Add Parking Spot</h3>

      <div class="mb-3">
        <label for="spot_number" class="form-label">Spot Number</label>
        <input
          v-model="form.spot_number"
          type="text"
          id="spot_number"
          class="form-control"
          required
        />
      </div>

      <div class="mb-3">
        <label for="lot_id" class="form-label">Parking Lot ID</label>
        <input
          v-model="form.lot_id"
          type="number"
          id="lot_id"
          class="form-control"
          required
        />
      </div>

      <div class="mb-3">
        <label for="status" class="form-label">Status</label>
        <select v-model="form.status" id="status" class="form-select" required>
          <option value="A">Available</option>
          <option value="O">Occupied</option>
        </select>
      </div>

      <button type="submit" class="btn btn-primary w-100">Add Spot</button>
    </form>

  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "AddSpot",

  data() {
    return {
      form: {
        spot_number: "",
        lot_id: "",
        status: "A"
      }
    };
  },

  methods: {
    async addSpot() {
      try {
        const token = localStorage.getItem("token");

        const response = await axios.post(
          "http://127.0.0.1:5000/api/spots",
          this.form,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        alert(response.data.message || "Spot added successfully!");
        this.$router.push("/adminhome");

      } catch (err) {
        alert(err.response?.data?.message || "Failed to add parking spot");
      }
    }
  }
};
</script>

<style scoped>
nav {
  display: flex;
  gap: 20px;
}

form {
  background: #ffffff;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0px 0px 8px rgba(0, 0, 0, 0.1);
}
</style>
