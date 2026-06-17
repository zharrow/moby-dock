import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// En `npm run dev`, on proxy /api vers le backend FastAPI local.
// En production (image Docker), c'est Nginx qui s'en charge (voir nginx.conf).
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
