import { defineConfig } from "astro/config";
import react from "@astrojs/react";
import mdx from "@astrojs/mdx";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  integrations: [react(), mdx()],
  output: "static",
  site: "https://anishasid.pages.dev",
  vite: {
    plugins: [tailwindcss()],
    build: { assetsInlineLimit: 0 }
  }
});
