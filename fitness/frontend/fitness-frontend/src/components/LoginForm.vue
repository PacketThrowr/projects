<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <h1>Welcome Back!</h1>
        <p>Please log in to access your account</p>
      </div>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">Username</label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            placeholder="Enter your username"
          />
        </div>
        <div class="input-group">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            placeholder="Enter your password"
          />
        </div>
        <div class="button-group">
          <button type="submit" :disabled="loading" class="login-button">
            <span v-if="loading">Loading...</span>
            <span v-else>Login</span>
          </button>
          <button type="button" @click="handleSignUp" class="signup-button">
            Sign Up
          </button>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL } from "../config"; // Import the global API base URL

export default {
  data() {
    return {
      username: "", // Replaced email with username
      password: "",
      loading: false,
      error: null,
    };
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = null;

      try {
        const response = await fetch(`${API_BASE_URL}/api/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username: this.username, password: this.password }),
        });

        if (!response.ok) {
          throw new Error("Invalid login credentials");
        }

        const data = await response.json();
        localStorage.setItem("token", data.token); // Store the token for future requests
        this.$router.push("/dashboard"); // Redirect to a dashboard or another page
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
    handleSignUp() {
      this.$router.push("/signup"); // Navigate to the signup page
    },
  },
};
</script>

<style scoped>
/* Center the login container */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--background-color);
  color: var(--text-color);
  padding: 2rem;
  box-sizing: border-box;
}

/* Login form content */
.login-content {
  max-width: 400px;
  width: 100%;
  padding: 2rem;
  background-color: var(--menu-bar-color);
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

/* Header section */
.login-header {
  margin-bottom: 2rem;
}

.login-header h1 {
  font-size: 1.8rem;
  margin: 0;
}

.login-header p {
  font-size: 1rem;
  margin: 0.5rem 0 1.5rem;
}

.login-image {
  max-width: 100%;
  height: auto;
  margin: 0 auto 1rem;
  border-radius: 8px;
}

/* Form elements */
.input-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.input-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--text-color);
  border-radius: 4px;
  font-size: 1rem;
  color: var(--text-color);
  background-color: var(--background-color);
  box-sizing: border-box;
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

/* Button group */
.button-group {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
}

button {
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.login-button {
  background-color: #4caf50;
  color: white;
}

.signup-button {
  background-color: transparent;
  color: var(--menu-bar-text-color);
  border: 1px solid var(--menu-bar-text-color);
}

.signup-button:hover {
  background-color: var(--menu-bar-text-color);
  color: var(--background-color);
}

/* Error message */
.error {
  color: red;
  margin-top: 1rem;
  font-size: 0.9rem;
}
</style>
