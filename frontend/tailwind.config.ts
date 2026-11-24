import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: { 950: "#07080b", 900: "#0b0d12", 850: "#0e1117", 800: "#12151c" },
        line: "#1e2430",
        muted: "#8b93a7",
        accent: { DEFAULT: "#3b82f6", soft: "#60a5fa" },
        ok: "#34d399",
        warn: "#fbbf24",
        crit: "#f87171",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
