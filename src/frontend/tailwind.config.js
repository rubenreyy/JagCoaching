/** @type {import('tailwindcss').Config} */
export default {
    content: [
      "./index.html",
      "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
      extend: {
        fontFamily: {
          mono: ['IBM Plex Mono', 'monospace'],
        },
        colors: {
          primary: "#0500FF",
          border: "hsl(var(--border))",
          background: "hsl(var(--background))",
          foreground: "hsl(var(--foreground))",
        },
        container: {
          center: true,
          padding: "2rem",
          screens: {
            "2xl": "1400px",
          },
        },
      },
    },
    plugins: [],
  }