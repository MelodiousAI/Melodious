import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    // The score engraver and MIDI player are lazy feature chunks; warn only if
    // a built chunk grows beyond those known library payloads.
    chunkSizeWarningLimit: 1400,
  },
  server: {
    port: 5173,
  },
})
