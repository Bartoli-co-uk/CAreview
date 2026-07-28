import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Builds straight into ../web with fixed, predictable filenames so
// server.py's explicit STATIC_FILES allowlist (no wildcard/hashed-file
// serving) can name every servable path exactly. emptyOutDir is false so
// web/sample-data.json (untouched, hand-committed fixture) survives a build.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../web",
    emptyOutDir: false,
    modulePreload: false,
    assetsDir: ".",
    rollupOptions: {
      output: {
        entryFileNames: "index.js",
        chunkFileNames: "index.js",
        assetFileNames: "index[extname]",
      },
    },
  },
});
