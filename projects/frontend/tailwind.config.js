/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'algorand': {
          DEFAULT: '#00D4AA',
          dark: '#00B794',
        }
      }
    },
  },
  plugins: [],
}
