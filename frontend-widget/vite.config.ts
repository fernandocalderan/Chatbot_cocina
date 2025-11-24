import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  build: {
    lib: {
      entry: "src/main.jsx",
      name: "OpunnenceWidget",
      fileName: () => `chat-widget.js`,
      formats: ["umd"],
    },
    rollupOptions: {
      external: ["react", "react-dom"],
      output: {
        globals: {
          react: "React",
          "react-dom": "ReactDOM",
        },
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith(".css")) {
            return "chat-widget.css";
          }
          return "[name].[ext]";
        },
      },
    },
  },
  test: {
    environment: "jsdom",
  },
});
