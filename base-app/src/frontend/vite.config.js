import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': 'http://localhost:3000',  // Must be localhost, NOT 'backend'
      '/health': 'http://localhost:3000',
      '/media': 'http://localhost:3000'
    }
  },
  build: { outDir: 'dist', sourcemap: false }
})