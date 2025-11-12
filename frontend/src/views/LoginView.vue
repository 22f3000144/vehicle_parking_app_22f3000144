<template>
  <div class="container mt-5" style="max-width: 450px;">
    <h3 class="mb-3 text-center">Login</h3>
    <div class="card p-4 shadow-sm">
      <form @submit.prevent="login">
        <div class="mb-3">
          <input v-model="data.username" type="text" placeholder="username" class="form-control" required />
        </div>
        <div class="mb-3">
          <input v-model="data.password" type="password" placeholder="password" class="form-control" required />
        </div>
        <button @click="login" type="submit" class="btn btn-dark w-100">login</button>
      </form>
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
        password: ""
      }
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post("http://127.0.0.1:5000/login", this.data);
        alert(response.data.msg);
        const token = response.data.token;
        localStorage.setItem("token", token);
      } catch (err) {
        alert(err.response?.data?.msg || "Login failed");
      }
    }
  }
};
</script>
