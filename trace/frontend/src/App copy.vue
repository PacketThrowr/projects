<template>
  <div class="container">
    <h1>HTTP Probe</h1>

    <form @submit.prevent="submit">
      <input v-model="url" placeholder="https://example.com" required />
      <select v-model="method">
        <option>GET</option>
        <option>POST</option>
        <option>HEAD</option>
      </select>
      <select v-model="type">
        <option value="http">HTTP</option>
        <option value="https">HTTPS</option>
        <!-- Later: TCP, UDP, etc. -->
      </select>
      <button type="submit">Run Test</button>
    </form>

    <div v-if="submitted" class="success">✅ Test job submitted for: {{ url }}</div>
    <div v-if="error" class="error">❌ {{ error }}</div>

    <h2>Recent Results</h2>
    <button @click="fetchResults">🔄 Refresh</button>

    <table v-if="results.length" class="results">
      <thead>
        <tr>
          <th>URL</th>
          <th>Method</th>
          <th>Status</th>
          <th>Latency (ms)</th>
          <th>DNS</th>
          <th>TCP</th>
          <th>SSL</th>
          <th>Recv</th>
          <th>Success</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(r, index) in results" :key="index">
          <td>{{ r.url }}</td>
          <td>{{ r.method }}</td>
          <td>{{ r.status_code }}</td>
          <td>{{ r.elapsed_ms?.toFixed(1) || '-' }}</td>
          <td :class="{ green: r.dns_ok, red: r.dns_ok === false }">{{ r.dns_ok ? '✅' : '❌' }}</td>
          <td :class="{ green: r.tcp_ok, red: r.tcp_ok === false }">{{ r.tcp_ok ? '✅' : '❌' }}</td>
          <td :class="{ green: r.ssl_ok, red: r.ssl_ok === false }">{{ r.ssl_ok ? '✅' : '❌' }}</td>
          <td :class="{ green: r.recv_ok, red: r.recv_ok === false }">{{ r.recv_ok ? '✅' : '❌' }}</td>
          <td :class="{ green: r.success, red: !r.success }">{{ r.success ? '✅' : '❌' }}</td>
        </tr>
      </tbody>
    </table>

    <p v-else>No results yet.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const url = ref('')
const method = ref('GET')
const type = ref('https') // default to HTTPS
const submitted = ref(false)
const error = ref('')
const results = ref([])

async function submit() {
  submitted.value = false
  error.value = ''

  try {
    const res = await fetch('http://localhost:8000/probe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: url.value,
        method: method.value,
        type: type.value,
      }),
    })

    const data = await res.json()
    if (res.ok && data.queued) {
      submitted.value = true
      fetchResults()
    } else {
      error.value = data.detail || 'Unknown error submitting job.'
    }
  } catch (e) {
    error.value = e.message
  }
}

async function fetchResults() {
  try {
    const res = await fetch('http://localhost:8000/results')
    const data = await res.json()
    results.value = data
  } catch (e) {
    console.error('Failed to fetch results:', e)
  }
}

onMounted(fetchResults)
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 2rem auto;
  padding: 1.5rem;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-family: sans-serif;
}

input, select {
  padding: 0.5rem;
  margin-right: 1rem;
  font-size: 1rem;
  width: 300px;
}

button {
  padding: 0.5rem 1rem;
  font-size: 1rem;
  margin-top: 1rem;
}

.success { color: green; margin-top: 1rem; }
.error { color: red; margin-top: 1rem; }

table.results {
  margin-top: 2rem;
  border-collapse: collapse;
  width: 100%;
}

table.results th, table.results td {
  border: 1px solid #ccc;
  padding: 0.5rem;
  text-align: left;
}

.green { color: green; }
.red { color: red; }
</style>
