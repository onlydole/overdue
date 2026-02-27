/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
  ],
  theme: {
    extend: {
      colors: {
        pixel: {
          bg: '#0f0e17',
          surface: '#1a1a2e',
          card: '#232342',
          border: '#3d3d6b',
          highlight: '#4a4a7a',
        },
        parchment: { light: '#fff8ee', DEFAULT: '#f0e6d3', dark: '#d4c4a8' },
        gold: { light: '#ffe9a0', DEFAULT: '#f0c543', dark: '#c49b22' },
        ink: { light: '#8b8b9e', DEFAULT: '#5a5a7a', dark: '#2e2e4a' },
        dewey: {
          pristine: '#5cdb5c',
          good: '#a0d468',
          attention: '#f6bb42',
          overdue: '#e8563e',
          lost: '#9e1b1b',
        },
        badge: { common: '#7eb5e3', rare: '#b76ef0', legendary: '#f0c543' },
        streak: '#f07a3e',
      },
      fontFamily: {
        pixel: ['"Press Start 2P"', 'cursive'],
        retro: ['"VT323"', 'monospace'],
      },
    },
  },
  plugins: [],
}
