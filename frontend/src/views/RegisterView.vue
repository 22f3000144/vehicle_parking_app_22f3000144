<template>
  <div class="container mt-5" style="max-width: 500px;">
    <h3 class="text-center mb-3">Register</h3>
    <div class="card p-4 shadow-sm">
      <form @submit.prevent="register">
        <div class="mb-3">
          <input v-model="data.username" type="text" placeholder="username" class="form-control" required />
        </div>

        <div class="mb-3">
          <input v-model="data.email" type="email" placeholder="email" class="form-control" required />
        </div>

        <div class="mb-3">
          <input v-model="data.model" type="text" placeholder="vehicle model" class="form-control" />
        </div>

        <div class="mb-3">
          <input v-model="data.password" type="password" placeholder="password" class="form-control" required />
        </div>

        <button @click="register" type="submit" class="btn btn-primary w-100">Register</button>
      </form>

      <div class="text-center mt-3">
        <router-link to="/login">Already have an account? Login</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      data: {
        username: "",
        email: "",
        model: "",
        password: ""
      }
    };
  },
  methods: {
    async register() {
      try {
        const response = await axios.post("http://127.0.0.1:5000/register", this.data);
        alert(response.data.message || "Registration successful!");
        this.$router.push("/login");
      } catch (err) {
        alert(err.response?.data?.message || "Registration failed");
      }
    }
  }
};
</script>
