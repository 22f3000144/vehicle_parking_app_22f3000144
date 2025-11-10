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

        <button class="btn btn-warning w-100">Update</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import axios from "axios"
import { ref, onMounted } from "vue"
import { useRoute, useRouter } from "vue-router"

const router = useRouter()
const route = useRoute()
const lot = ref({
  prime_location_name: "",
  price: "",
  address: "",
  pin_code: "",
  max_spot: ""
})

onMounted(fetchLot)

async function fetchLot() {
  try {
    const token = localStorage.getItem("token")
    const res = await axios.get(`/api/lots/${route.params.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    lot.value = res.data
  } catch (err) {
    alert(err.response?.data?.message || "Failed to load lot details.")
  }
}

async function updateLot() {
  try {
    const token = localStorage.getItem("token")
    await axios.put(`/api/lots/${route.params.id}`, lot.value, {
      headers: { Authorization: `Bearer ${token}` }
    })
    alert("Parking lot updated successfully.")
    router.push("/admin")
  } catch (err) {
    alert(err.response?.data?.message || "Failed to update parking lot.")
  }
}
</script>
