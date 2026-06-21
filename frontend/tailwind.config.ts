import type { Config } from 'tailwindcss';
export default {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        deep: '#0F172A',
        indigo: '#4F46E5',
        cyan: '#06B6D4',
        surface: '#180e49',
      },
      boxShadow: {
        glass: '0 25px 80px rgba(15, 23, 42, 0.12)',
      },
      fontFamily: {
        sans: ['Inter', 'Poppins', 'sans-serif'],
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
} satisfies Config;
