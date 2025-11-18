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

        <button type="submit" class="btn btn-warning w-100">Create</button>

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
      }
    };
  },

  methods: {
    async createLot() {
      try {
        const token = localStorage.getItem("token");

        const response = await axios.post(
          "http://127.0.0.1:5000/api/lots",
          this.form,
          {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer' + token 
            }   
          }
        );
        
        alert(response.data.message || "Parking lot created!");

        this.$router.push("/adminhome");

      } catch (err) {
        console.log(err);
        alert(err.response?.data?.message);
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
