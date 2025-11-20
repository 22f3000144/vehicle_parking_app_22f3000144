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
              {{ lot.prime_location_name }} — ₹{{ lot.price }}/hr ({{ lot.address }})
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
    this.checkActiveReservation()
    this.fetchLots()
  },

  methods: {
    // Prevent booking if user already has a reservation
    async checkActiveReservation() {
      try {
        const token = localStorage.getItem("token")
        const res = await axios.get("http://localhost:5000/api/user/status", {
          headers: { Authorization: `Bearer ${token}` }
        })

        if (res.data.active) {
          this.errorMessage = `You already have a reserved spot (#${res.data.spot_number}) at ${res.data.lot_name}.`
        }
      } catch (err) {
        // ignore minor errors
      }
    },

    // Load all parking lots
    async fetchLots() {
      try {
        const token = localStorage.getItem("token")
        const res = await axios.get("http://localhost:5000/api/lots", {
          headers: { Authorization: `Bearer ${token}` },
        })
        this.lots = res.data
      } catch (err) {
        this.errorMessage = "Failed to load parking lots."
      }
    },

    // Reserve a spot correctly using spot_id
    async reserveSpot() {
      this.successMessage = ""
      this.errorMessage = ""

      if (!this.selectedLot) {
        this.errorMessage = "Please select a parking lot."
        return
      }

      // Get the selected lot object
      const lot = this.lots.find(l => l.id === this.selectedLot)

      if (!lot || !lot.spots) {
        this.errorMessage = "Invalid lot selected."
        return
      }

      // Pick the first free spot
      const freeSpot = lot.spots.find(s => s.status === "A")

      if (!freeSpot) {
        this.errorMessage = "No available spots in this lot."
        return
      }

      // Make reservation
      try {
        const token = localStorage.getItem("token")

        const res = await axios.post(
          "http://localhost:5000/api/reserve",
          { spot_id: freeSpot.id },
          { headers: { Authorization: `Bearer ${token}` } }
        )

        this.successMessage = `🅿️ Your spot is reserved!
Spot #: ${freeSpot.spot_number}
Parking Lot: ${lot.prime_location_name}
Entry Time: ${new Date().toLocaleString()}`

      } catch (err) {
        this.errorMessage = err.response?.data?.message || "Reservation failed."
      }
    },
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
