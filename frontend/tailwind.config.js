/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        parchment: {
          50: '#fdfbf5',
          100: '#f7f0dd',
          200: '#efe4c6',
          300: '#e3d3a6',
        },
        ink: {
          700: '#3a2f22',
          800: '#2a2118',
          900: '#1c1610',
        },
        forest: {
          600: '#2f4c3b',
          700: '#233a2d',
          800: '#1a2c22',
        },
        walnut: {
          600: '#5c4330',
          700: '#4b3423',
          800: '#3a2819',
        },
        brass: {
          400: '#c9a86a',
          500: '#b08d4f',
          600: '#8f7040',
        },
      },
      fontFamily: {
        serif: ['"Playfair Display"', 'Georgia', 'serif'],
        sans: ['"Source Sans 3"', '"Segoe UI"', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        shelf: '0 2px 0 0 rgba(74, 52, 35, 0.35)',
        book: '0 6px 16px -6px rgba(28, 22, 16, 0.35)',
      },
    },
  },
  plugins: [],
}
