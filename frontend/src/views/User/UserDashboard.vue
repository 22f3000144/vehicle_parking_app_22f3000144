<template>
  <div class="container mt-4" id="user-dashboard">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="text-primary">Welcome, {{ username }}!</h3>
      <button @click="logout" class="btn btn-outline-danger btn-sm">Logout</button>
    </div>

    <p class="text-muted">Manage your parking activity below.</p>

    <!-- Loading Spinner -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Parking Lot List -->
    <div v-else>
      <div v-if="parkingLots.length" class="table-responsive">
        <table class="table table-bordered table-striped shadow-sm bg-white">
          <thead class="table-dark text-center">
            <tr>
              <th>ID</th>
              <th>Location</th>
              <th>Price/hr</th>
              <th>Address</th>
              <th>Pin Code</th>
              <th>Available Spots</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody class="text-center">
            <tr v-for="lot in parkingLots" :key="lot.id">
              <td>{{ lot.id }}</td>
              <td>{{ lot.prime_location_name }}</td>
              <td>₹{{ lot.price }}</td>
              <td>{{ lot.address }}</td>
              <td>{{ lot.pin_code }}</td>
              <td>{{ lot.available_spots }}</td>
              <td>
                <button
                  v-if="!lot.reserved"
                  class="btn btn-success btn-sm"
                  @click="reserveSpot(lot.id)"
                >
                  Reserve
                </button>
                <button
                  v-else
                  class="btn btn-warning btn-sm"
                  @click="releaseSpot(lot.id)"
                >
                  Release
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-else class="text-muted text-center">
        No parking lots available at the moment.
      </p>
    </div>
  </div>
</template>

<script setup>
import axios from "axios"
import { ref, onMounted } from "vue"
import { useRouter } from "vue-router"

const router = useRouter()
const username = ref(localStorage.getItem("username") || "User")
const parkingLots = ref([])
const loading = ref(true)

// ✅ Fetch all parking lots from backend
async function fetchParkingLots() {
  try {
    const token = localStorage.getItem("token")
    if (!token) {
      router.push("/login")
      return
    }

    const res = await axios.get("http://127.0.0.1:5000/api/lots", {
      headers: { Authorization: `Bearer ${token}` },
    })

    // Assign dummy available spots until backend provides count
    parkingLots.value = res.data.map((lot) => ({
      ...lot,
      available_spots: lot.max_spot, // placeholder
      reserved: false,
    }))
  } catch (err) {
    alert(err.response?.data?.message || "Failed to load parking lots.")
  } finally {
    loading.value = false
  }
}

// ✅ Reserve a parking spot
async function reserveSpot(lotId) {
  try {
    const token = localStorage.getItem("token")
    const res = await axios.post(
      "http://127.0.0.1:5000/api/reserve",
      { lot_id: lotId },
      { headers: { Authorization: `Bearer ${token}` } }
    )

    if (res.status === 200) {
      const lot = parkingLots.value.find((l) => l.id === lotId)
      if (lot) {
        lot.reserved = true
        lot.available_spots = Math.max(0, lot.available_spots - 1)
      }
      alert(`✅ Spot reserved successfully in lot #${lotId}`)
    }
  } catch (err) {
    alert(err.response?.data?.message || "Failed to reserve spot.")
  }
}

// ✅ Release a parking spot
async function releaseSpot() {
  try {
    const token = localStorage.getItem("token")
    const res = await axios.post(
      "http://127.0.0.1:5000/api/release",
      {},
      { headers: { Authorization: `Bearer ${token}` } }
    )

    if (res.status === 200) {
      // Reset reservation flags locally
      parkingLots.value.forEach((lot) => {
        if (lot.reserved) {
          lot.reserved = false
          lot.available_spots += 1
        }
      })

      const { duration_minutes, cost } = res.data
      alert(
        `🅿️ Spot released.\nDuration: ${duration_minutes} mins\nCost: ₹${cost}`
      )
    }
  } catch (err) {
    alert(err.response?.data?.message || "Failed to release spot.")
  }
}

// ✅ Logout
function logout() {
  localStorage.removeItem("token")
  localStorage.removeItem("role")
  localStorage.removeItem("username")
  router.push("/login")
}

onMounted(() => {
  if (!localStorage.getItem("token") || localStorage.getItem("role") !== "user") {
    router.push("/login")
  } else {
    fetchParkingLots()
  }
})
</script>

<style scoped>
#user-dashboard {
  min-height: 100vh;
}

.table {
  font-size: 0.9rem;
}

.text-center {
  text-align: center;
}

@media (max-width: 768px) {
  #user-dashboard {
    padding: 1rem;
  }

  .table {
    font-size: 0.85rem;
  }

  h3 {
    font-size: 1.2rem;
  }

  .btn {
    font-size: 0.8rem;
  }
}
</style>
