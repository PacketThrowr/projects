import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '10.1.10.168', // Bind to your server's IP address
    port: 5173,          // Default Vite port
    open: true,          // Automatically open in a browser (optional)
  },
});
