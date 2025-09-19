/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./App.{js,jsx,ts,tsx}", "./screens/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        'golden-sandstone': '#8A724C',
        'amber-tresses': '#B99668', 
        'silken-dune': '#DCC9A7',
        'champagne-veil': '#EDE2CC',
        'ivory-whisper': '#F7F3E8',
      },
    },
  },
  plugins: [],
}