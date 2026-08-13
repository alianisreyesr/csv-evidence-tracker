/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        pharma: {
          blue: '#003366',
          teal: '#007A7A',
          green: '#2E7D32',
          amber: '#F59E0B',
          red: '#DC2626'
        }
      }
    }
  },
  plugins: []
}
