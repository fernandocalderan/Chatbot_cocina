import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig(({ mode }) => ({
  plugins: [react()],

  define: {
    // Evita builds de React en modo producción dentro de vitest (act()).
    'process.env.NODE_ENV': JSON.stringify(mode === 'test' ? 'development' : 'production'),
    'process.env': {},
  },

  build: {
    lib: {
      entry: 'src/main.jsx',
      name: 'ChatWidget',
      fileName: () => 'chat-widget.js',
      formats: ['es'],
    },
    rollupOptions: {
      external: [],
    },
  },
  test: {
    environment: 'jsdom',
  },
}))
