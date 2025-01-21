import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  optimizeDeps: {
    needsInterop: ['@mapbox/mapbox-gl-directions'],

    include: ['mapbox-gl', '@mapbox/mapbox-gl-directions'],
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      'mapbox-gl': 'mapbox-gl/dist/mapbox-gl.js',
      

    },
  },
})
