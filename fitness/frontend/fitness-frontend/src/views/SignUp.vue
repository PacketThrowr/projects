<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <h1>Create Account</h1>
        <p>Please fill in your details to sign up</p>
      </div>
      <form @submit.prevent="handleSignUp">
        <div class="input-group">
          <label for="username">Username</label>
          <input
            type="text"
            id="username"
            v-model="username"
            required
            placeholder="Choose a username"
          />
        </div>
        <div class="input-group">
          <label for="email">Email</label>
          <div class="password-input-wrapper">
            <input
              type="email"
              id="email"
              v-model="email"
              required
              placeholder="Enter your email"
              :class="{ 'invalid': email && !isValidEmail }"
            />
            <span v-if="email && isValidEmail" class="check-icon">✓</span>
          </div>
          <span v-if="email && !isValidEmail" class="error-text">Please enter a valid email address</span>
        </div>
        <div class="input-group">
          <label for="password">Password</label>
          <input
            type="password"
            id="password"
            v-model="password"
            required
            placeholder="Create a password"
          />
        </div>
        <div class="input-group">
          <label for="confirmPassword">Confirm Password</label>
          <div class="password-input-wrapper">
            <input
              type="password"
              id="confirmPassword"
              v-model="confirmPassword"
              required
              placeholder="Verify your password"
            />
            <span v-if="showCheckmark" class="check-icon">✓</span>
          </div>
        </div>
        <div class="button-group">
          <button type="submit" :disabled="loading" class="login-button">
            <span v-if="loading">Loading...</span>
            <span v-else>Sign Up</span>
          </button>
          <button type="button" @click="handleLogin" class="signup-button">
            Back to Login
          </button>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL } from "../config";

export default {
  computed: {
    passwordsMatch() {
      return Boolean(this.password && this.confirmPassword && this.password === this.confirmPassword);
    },
    showCheckmark() {
      return this.passwordsMatch && this.password.length >= 1;
    },
    isValidEmail() {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(this.email);
    }
  },
  data() {
    return {
      username: "",
      email: "",
      password: "",
      confirmPassword: "",
      loading: false,
      error: null,
    };
  },
  methods: {
    async handleSignUp() {
      this.loading = true;
      this.error = null;

      try {
        const response = await fetch(`${API_BASE_URL}/api/users`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            username: this.username,
            email: this.email,
            password: this.password 
          }),
        });

        if (!response.ok) {
          throw new Error("Registration failed");
        }

        // Login after successful registration
        const formData = new FormData();
        formData.append('username', this.username);
        formData.append('password', this.password);

        const loginResponse = await fetch(`${API_BASE_URL}/auth/jwt/login`, {
          method: 'POST',
          body: formData
        });

        if (!loginResponse.ok) {
          throw new Error('Login failed after registration');
        }

        const { access_token } = await loginResponse.json();
        localStorage.setItem('token', access_token);
        this.$router.push('/create-profile');
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
    handleLogin() {
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
/* Reuse the same styles from the login component */
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

.login-content {
  max-width: 400px;
  width: 100%;
  padding: 2rem;
  background-color: var(--menu-bar-color);
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

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

.error {
  color: red;
  margin-top: 1rem;
  font-size: 0.9rem;
}

.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.check-icon {
  position: absolute;
  right: 10px;
  color: #4caf50;
  font-weight: bold;
}

.error-text {
  color: red;
  font-size: 0.8rem;
  margin-top: 0.25rem;
  display: block;
}

.invalid {
  border-color: red !important;
}
</style>