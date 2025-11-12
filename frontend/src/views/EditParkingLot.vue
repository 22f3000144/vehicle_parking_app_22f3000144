<template>
  <div class="container mt-4" style="max-width: 600px;">
    <div class="card shadow-sm p-4">
      <h3 class="text-center mb-3">Edit Parking Lot</h3>
      <form @submit.prevent="updateLot">
        <div class="mb-3">
          <label>Prime Location</label>
          <input v-model="lot.prime_location_name" class="form-control" required />
        </div>

        <div class="mb-3">
          <label>Price (₹/hour)</label>
          <input type="number" v-model.number="lot.price" class="form-control" required />
        </div>

        <div class="mb-3">
          <label>Address</label>
          <input v-model="lot.address" class="form-control" required />
        </div>

        <div class="mb-3">
          <label>Pin Code</label>
          <input v-model="lot.pin_code" class="form-control" required />
        </div>

        <div class="mb-3">
          <label>Max Spots</label>
          <input type="number" v-model.number="lot.max_spot" class="form-control" required />
        </div>

        <button class="btn btn-warning w-100" type="submit">Update</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      lot: {
        prime_location_name: "",
        price: "",
        address: "",
        pin_code: "",
        max_spot: ""
      }
    };
  },
  methods: {
    async fetchLot() {
      try {
        const token = localStorage.getItem("token");
        const id = this.$route.params.id;
        const res = await axios.get(`http://127.0.0.1:5000/lots/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.lot = res.data;
      } catch (err) {
        alert(err.response?.data?.message || "Failed to load lot details.");
      }
    },
    async updateLot() {
      try {
        const token = localStorage.getItem("token");
        const id = this.$route.params.id;
        await axios.put(`http://127.0.0.1:5000/lots/${id}`, this.lot, {
          headers: { Authorization: `Bearer ${token}` }
        });
        alert("Parking lot updated successfully.");
        this.$router.push("/admin");
      } catch (err) {
        alert(err.response?.data?.message || "Failed to update parking lot.");
      }
    }
  },
  mounted() {
    this.fetchLot();
  }
};
</script>
