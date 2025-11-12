<template>
  <div class="container mt-4" style="max-width: 600px;">
    <div class="card shadow-sm p-4">
      <h3 class="text-center mb-3">Create Parking Lot</h3>
      <form @submit.prevent="createLot">
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

        <button class="btn btn-success w-100">Create</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from "axios"

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
    }
  },
  methods: {
    async createLot() {
      try {
        const token = localStorage.getItem("token")
        await axios.post("http://127.0.0.1:5000/api/lots", this.lot, {
          headers: { Authorization: `Bearer ${token}` }
        })
        alert("Parking lot created successfully.")
        this.$router.push("/admin")
      } catch (err) {
        alert(err.response?.data?.message || "Failed to create parking lot.")
      }
    }
  }
}
</script>
