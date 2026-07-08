/**
 * vite.config.js
 * Proxies /api and /media to the Django backend during development so the
 * frontend can call relative paths (no hardcoded localhost:8000 in code).
 */
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:8000", // use 127.0.0.1, not localhost, on Windows
        changeOrigin: true,
      },
      "/media": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
      },
    },
  },
});
