<template>
  <div class="login-container">
    <div class="login-content">
      <div class="login-header">
        <h1>Create Profile</h1>
        <p>Please fill in your profile details</p>
      </div>
      <form @submit.prevent="handleProfileCreation">
        <div class="input-group">
          <label for="name">Name</label>
          <input
            type="text"
            id="name"
            v-model="profile.name"
            placeholder="Default Profile"
          />
        </div>

        <div class="input-group">
          <label for="gender">Gender</label>
          <select id="gender" v-model="profile.gender">
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="not_applicable">Not Applicable</option>
          </select>
        </div>

        <div class="input-group">
          <label for="country">Country</label>
          <select id="country" v-model="profile.country" @change="updateUnits">
            <option value="US">United States</option>
            <option value="UK">United Kingdom</option>
            <option value="CA">Canada</option>
            <option value="AU">Australia</option>
            <option value="IN">India</option>
            <option value="FR">France</option>
            <option value="DE">Germany</option>
          </select>
        </div>

        <div class="input-group">
          <label for="units">Measurement System</label>
          <select id="units" v-model="profile.units">
            <option value="imperial">Imperial</option>
            <option value="metric">Metric</option>
          </select>
        </div>

        <div class="input-group">
          <label for="weight">Weight {{ profile.units === 'imperial' ? '(lbs)' : '(kg)' }}</label>
          <input
            type="number"
            id="weight"
            v-model="weight"
            required
            step="0.1"
          />
        </div>

        <div v-if="profile.units === 'imperial'" class="height-imperial">
          <div class="input-group">
            <label for="feet">Height (feet)</label>
            <input
              type="number"
              id="feet"
              v-model="profile.height_feet"
              required
              min="0"
            />
          </div>
          <div class="input-group">
            <label for="inches">Height (inches)</label>
            <input
              type="number"
              id="inches"
              v-model="profile.height_inches"
              required
              min="0"
              max="11"
            />
          </div>
        </div>

        <div v-else class="input-group">
          <label for="cm">Height (cm)</label>
          <input
            type="number"
            id="cm"
            v-model="profile.height_cm"
            required
            min="0"
          />
        </div>

        <div class="button-group">
          <button type="submit" :disabled="loading" class="login-button">
            <span v-if="loading">Loading...</span>
            <span v-else>Create Profile</span>
          </button>
        </div>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script>
import { API_BASE_URL } from "../config";

const COUNTRY_UNITS_MAP = {
  "US": "imperial",
  "UK": "imperial",
  "CA": "imperial",
  "AU": "metric",
  "IN": "metric",
  "FR": "metric",
  "DE": "metric",
};

export default {
  data() {
    return {
      profile: {
        name: "Default Profile",
        gender: "male",
        height_feet: 0,
        height_inches: 0,
        height_cm: 0,
        country: "US",
        units: "imperial",
      },
      weight: 0,
      loading: false,
      error: null
    };
  },
  methods: {
    updateUnits() {
      this.profile.units = COUNTRY_UNITS_MAP[this.profile.country];
    },
    async handleProfileCreation() {
      this.loading = true;
      this.error = null;

      try {
        const token = localStorage.getItem('token');
        const weightData = {
          date: new Date().toISOString(),
          value: parseFloat(this.weight),
          bmi: 0 // Backend will calculate this
        };

        const response = await fetch(`${API_BASE_URL}/api/profiles`, {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
          },
          body: JSON.stringify({
            ...this.profile,
            weight: [weightData]
          }),
        });

        if (!response.ok) {
          throw new Error("Profile creation failed");
        }

        await response.json();
        this.$router.push("/dashboard");
      } catch (err) {
        this.error = err.message;
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
/* Reuse the same base styles from login/signup */
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

.input-group input,
.input-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--text-color);
  border-radius: 4px;
  font-size: 1rem;
  color: var(--text-color);
  background-color: var(--background-color);
  box-sizing: border-box;
}

.height-imperial {
  display: flex;
  gap: 1rem;
}

.height-imperial .input-group {
  flex: 1;
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

.error {
  color: red;
  margin-top: 1rem;
  font-size: 0.9rem;
}
</style>