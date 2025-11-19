<template>
  <div>

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-black px-3">
      <a class="navbar-brand text-orange fw-bold" href="#">Admin Portal</a>
      <div class="navbar-nav">
        <router-link class="nav-link text-white" to="/adminhome">Home</router-link>
        <router-link class="nav-link text-white" to="/userlist">Users</router-link>
        <router-link class="nav-link text-white" to="/adminchart">Summary</router-link>
      </div>
    </nav>

    <!-- Form Section -->
    <div class="container mt-5 form-box shadow-lg p-4 bg-white rounded">
      <h2 class="mb-4 text-orange">Create Parking Lot</h2>

      <form @submit.prevent="createLot">

        <div class="mb-3">
          <label class="form-label">Location Name</label>
          <input v-model="form.prime_location_name" type="text" class="form-control" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Price/hr</label>
          <input v-model="form.price" type="number" class="form-control" step="0.01" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Address</label>
          <input v-model="form.address" type="text" class="form-control" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Pin Code</label>
          <input v-model="form.pin_code" type="text" class="form-control" required />
        </div>

        <div class="mb-3">
          <label class="form-label">Max Spots</label>
          <input v-model="form.max_spot" type="number" class="form-control" required />
        </div>

        <button type="submit" class="btn btn-warning w-100" :disabled="loading">
          <span v-if="loading">Creating...</span>
          <span v-else>Create</span>
        </button>

      </form>
    </div>

  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "AddParking",

  data() {
    return {
      form: {
        prime_location_name: "",
        price: "",
        address: "",
        pin_code: "",
        max_spot: ""
      },
      loading: false
    };
  },

  methods: {
      async createLot() {
        try {
          this.loading = true;

          const prime_location_name = this.form.prime_location_name;
          const address = this.form.address;
          const pin_code = this.form.pin_code;
          const price = parseFloat(this.form.price);
          const max_spot = parseInt(this.form.max_spot);

          const payload = { prime_location_name, price, address, pin_code, max_spot };
          console.log("Sending payload:", payload);

          const token = localStorage.getItem("token");
          if (!token) {
            alert("No token found. Please login again.");
            this.loading = false;
            return;
          }

          const response = await axios.post(
            "http://127.0.0.1:5000/api/lots",
            payload,
            {
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
              }
            }
          );

          alert(response.data.message);
          this.$router.push("/adminhome");

        } catch (err) {
          console.error(err);
        } finally {
          this.loading = false;
        }
      }
  }
};
</script>

<style scoped>
.text-orange {
  color: #00ffdd;
}

.btn-orange,
.btn-warning {
  background-color: orange;
  color: white;
  border: none;
}

.btn-orange:hover {
  background-color: rgb(255, 140, 0);
}

.form-box {
  max-width: 600px;
}
</style>
