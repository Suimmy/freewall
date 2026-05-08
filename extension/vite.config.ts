import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { crx } from '@crxjs/vite-plugin'
import manifest from './manifest.json' with { type: 'json' }
import path from 'node:path'

// @crxjs reads manifest.json and wires MV3 entry points (background, content, popup) automatically.
// strictPort required — content-script HMR pings must hit a stable known port.
export default defineConfig({
  plugins: [react(), crx({ manifest })],
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    port: 5173,
    strictPort: true,
    hmr: { port: 5173 },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    target: 'esnext',
  },
})
