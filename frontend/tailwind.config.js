/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bauhaus: {
          red: '#E3000B',
          yellow: '#FFD700',
          blue: '#003DA5',
          black: '#000000',
          white: '#FFFFFF',
          gray: {
            100: '#F5F5F5',
            200: '#E0E0E0',
            300: '#BDBDBD',
            400: '#9E9E9E',
            500: '#757575',
            600: '#616161',
            700: '#424242',
            800: '#303030',
            900: '#212121'
          }
        }
      },
      fontFamily: {
        bauhaus: ['Poppins', 'Jost', 'Inter', 'sans-serif'],
        body: ['Inter', '-apple-system', 'sans-serif']
      },
      borderWidth: {
        '3': '3px',
        '4': '4px',
        '5': '5px',
        '6': '6px'
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem'
      },
      boxShadow: {
        'bauhaus': 'none',
        'bauhaus-strong': '4px 4px 0px #000000'
      },
      animation: {
        'none': 'none'
      }
    },
  },
  plugins: [],
}
