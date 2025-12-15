import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],

  define: {
    'process.env.NODE_ENV': JSON.stringify('production'),
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
})
