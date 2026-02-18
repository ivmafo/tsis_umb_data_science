/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#1a237e", // Main blue from reference
          light: "#534bae",
          dark: "#000051",
        },
        glass: "rgba(255, 255, 255, 0.1)",
        glassBorder: "rgba(255, 255, 255, 0.2)",
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
