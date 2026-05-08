/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Twitter-inspired palette
        twitter: {
          blue: "#1d9bf0",
          dim: "#15202b",
          bg: "#ffffff",
          border: "#eff3f4",
          text: "#0f1419",
          muted: "#536471",
          hover: "#f7f9f9",
        },
        // Freewall score bands
        risk: {
          high: "#ef4444",     // red-500
          caution: "#eab308",  // yellow-500
          safe: "#22c55e",     // green-500
        },
      },
      fontFamily: {
        sans: ["-apple-system", "BlinkMacSystemFont", "Inter", "Sarabun", "sans-serif"],
      },
    },
  },
  plugins: [],
};
