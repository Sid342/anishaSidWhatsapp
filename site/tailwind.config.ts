import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{astro,html,js,jsx,ts,tsx,md,mdx}"],
  theme: {
    extend: {
      colors: {
        midnight: { 950: "#08060d", 900: "#0d0a16", 800: "#13101e" },
        gold:     { 400: "#d4af6a", 500: "#c89a4a", 600: "#a87a2e" },
        paper:    { 50:  "#f4ecd8", 100: "#ede0c2", 200: "#dcc89a" },
        ink:      { 900: "#1b1208", 700: "#3a2716" }
      },
      fontFamily: {
        serif:  ["EB Garamond", "Georgia", "serif"],
        hand:   ["Caveat", "cursive"],
        mono:   ["JetBrains Mono", "monospace"]
      },
      boxShadow: {
        paper: "0 2px 12px rgba(0,0,0,0.55), inset 0 0 24px rgba(120,90,40,0.08)"
      }
    }
  },
  plugins: []
} satisfies Config;
