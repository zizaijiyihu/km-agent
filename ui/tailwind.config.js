/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4F46E5',
        secondary: '#F3F4F6',
        'light-blue': '#f0f8ff',
      },
    },
  },
  plugins: [],
}
