import path from "node:path";
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: { "@": path.resolve(import.meta.dirname, "./src") },
    },
    server: {
      // Forward /api requests to FastAPI so the browser sees a single origin (no CORS in dev)
      proxy: {
        "/api": env.API_PROXY_TARGET ?? "http://localhost:8000",
      },
    },
  };
});
