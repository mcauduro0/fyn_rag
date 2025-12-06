/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Neo-Brutalist Dark Theme
        'fyn-bg': '#0a0a0a',
        'fyn-surface': '#141414',
        'fyn-border': '#2a2a2a',
        'fyn-accent': '#00ff88',
        'fyn-accent-dim': '#00cc6a',
        'fyn-warning': '#ffcc00',
        'fyn-danger': '#ff4444',
        'fyn-text': '#ffffff',
        'fyn-text-dim': '#888888',
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
