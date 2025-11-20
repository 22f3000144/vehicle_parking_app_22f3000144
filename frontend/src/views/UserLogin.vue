<template> 
  <div class="container mt-5" style="max-width: 450px;">
    <h3 class="mb-3 text-center">Login</h3>
    <div class="card p-4 shadow-sm">
      <form @submit.prevent="login">
        <div class="mb-3">
          <input v-model="data.email" type="text" placeholder="email" class="form-control" required />
        </div>
        <div class="mb-3">
          <input v-model="data.password" type="password" placeholder="password" class="form-control" required />
        </div>
        <button type="submit" class="btn btn-dark w-100">login</button>
      </form>

    </div>
      <div class="text-center mt-3">
        <router-link to="/register">New Here ? Sine-In</router-link>
      </div>
      <div class="text-center mt-3">
        <router-link to="/adminlogin">Login as Admin</router-link>
      </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      data: { email: "", password: "" }
    };
  },

  methods: {
    async login() {
      try {
        const response = await axios.post("http://127.0.0.1:5000/api/login", this.data);

        if (response.data.role !== "user") {
          alert("Admins must login using the Admin Panel.");
          return;
        }

        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("role", response.data.role);
        localStorage.setItem("user_id", response.data.id);

        this.$router.push({ name: "userhome" });

      } catch (err) {
        alert(err.response?.data?.message || "Login failed");
      }
    }
  }
};
</script>