/** @type {import('tailwindcss').Config} */

export default {
  content: [
    "./index.html",
    "./*.{js,jsx}",
    "./components/**/*.{js,jsx}",
  ],

  theme: {
    extend: {
      colors: {
        ink: "#0b1120",
        panel: "#111827",
        panelLine: "#243047",
        paper: "#f8fafc",
        muted: "#94a3b8",
        signal: "#38bdf8",
        clear: "#34d399",
        alert: "#fb7185",
      },

      fontFamily: {
        body: ["Arial", "sans-serif"],
        case: ["Arial", "sans-serif"],
        data: ["Consolas", "monospace"],
      },

      boxShadow: {
        glow: "0 0 30px rgba(56, 189, 248, 0.08)",
      },
    },
  },

  plugins: [],
};