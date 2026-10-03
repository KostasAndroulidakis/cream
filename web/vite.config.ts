import fs from "node:fs";
import path from "node:path";
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// A trusted local certificate (made with mkcert, see README) switches the dev server to https:
// Enable Banking's production apps only redirect back to https URLs
const CERT_DIR = path.resolve(import.meta.dirname, ".cert");
const CERT_FILE = path.join(CERT_DIR, "localhost.pem");
const KEY_FILE = path.join(CERT_DIR, "localhost-key.pem");

function localHttps() {
  if (!fs.existsSync(CERT_FILE) || !fs.existsSync(KEY_FILE)) return undefined;
  return { cert: fs.readFileSync(CERT_FILE), key: fs.readFileSync(KEY_FILE) };
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: { "@": path.resolve(import.meta.dirname, "./src") },
    },
    server: {
      https: localHttps(),
      // Forward /api requests to FastAPI so the browser sees a single origin (no CORS in dev)
      proxy: {
        "/api": env.API_PROXY_TARGET ?? "http://localhost:8000",
      },
    },
  };
});
