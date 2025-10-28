/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        santa: {
          red: "#D7263D",
          green: "#21A179",
          gold: "#F9DC5C"
        }
      }
    }
  },
  plugins: []
};
