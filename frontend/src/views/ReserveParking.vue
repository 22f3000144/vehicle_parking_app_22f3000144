<template>
  <div class="p-4" style="background-color: white; color: black; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <!-- Navigation Bar -->
    <nav class="d-flex gap-3 mb-4" style="background-color: teal; padding: 10px 20px; border-radius: 5px;">
      <RouterLink to="/userhome" class="text-white fw-bold text-decoration-none">🏠 Home</RouterLink>
      <RouterLink to="/userchart" class="text-white fw-bold text-decoration-none">Summary</RouterLink>
     
    </nav>

    <!-- Main Container -->
    <div
      class="container"
      style="max-width: 700px; background-color: #f9f9f9; padding: 25px; border-radius: 10px; box-shadow: 0 0 10px rgba(64, 224, 208, 0.3);"
    >
      <h2 class="mb-4" style="color: teal; font-weight: 600;">Reserve a Parking Spot</h2>

      <form @submit.prevent="reserveSpot">
        <div class="mb-3">
          <label class="form-label fw-bold">Select Parking Lot</label>
          <select
            v-model="selectedLot"
            class="form-select"
            style="border: 2px solid teal; border-radius: 6px;"
          >
            <option disabled value="">-- Choose a Lot --</option>
            <option v-for="lot in lots" :key="lot.id" :value="lot.id">
              {{ lot.prime_location_name }} — ₹{{ lot.price }}/min ({{ lot.address }})
            </option>
          </select>
        </div>

        <button type="submit" class="btn w-100 fw-bold" style="background-color: #40e0d0; border: none;">
          Reserve
        </button>
      </form>

      <div v-if="successMessage" class="alert alert-success mt-4">
        {{ successMessage }}
      </div>
      <div v-if="errorMessage" class="alert alert-danger mt-4">
        {{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios"
import { useRouter } from "vue-router"

export default {
  name: "ReserveSpot",
  data() {
    return {
      lots: [],
      selectedLot: "",
      successMessage: "",
      errorMessage: "",
    }
  },
  mounted() {
    this.fetchLots()
  },
  methods: {
    async fetchLots() {
      try {
        const token = localStorage.getItem("token")
        const res = await axios.get("http://localhost:5000/api/lots", {
          headers: { Authorization: `Bearer ${token}` },
        })
        this.lots = res.data
      } catch (err) {
        this.errorMessage =
          err.response?.data?.message || "Failed to load parking lots."
      }
    },

    async reserveSpot() {
      if (!this.selectedLot) {
        this.errorMessage = "Please select a parking lot."
        return
      }

      try {
        const token = localStorage.getItem("token")
        const res = await axios.post(
          "http://localhost:5000/api/reserve",
          { lot_id: this.selectedLot },
          { headers: { Authorization: `Bearer ${token}` } }
        )

        this.successMessage = `✅ Reserved spot #${res.data.spot_number} at ${res.data.lot_name}.
        Entry time: ${res.data.entry_time}`
        this.errorMessage = ""
      } catch (err) {
        this.errorMessage = err.response?.data?.message || "Reservation failed."
        this.successMessage = ""
      }
    },
  },
  setup() {
    const router = useRouter()
    return { router }
  },
}
</script>

<style scoped>
@media (max-width: 768px) {
  .container {
    width: 100%;
    padding: 15px;
  }
}
</style>
