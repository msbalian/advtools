/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#f0f7ff',
                    100: '#e0f0fe',
                    200: '#bae0fd',
                    300: '#7bc8fb',
                    400: '#37aef8',
                    500: '#0c95eb',
                    600: '#0176cb',
                    700: '#025ea5',
                    800: '#065087',
                    900: '#0c426e',
                },
                secondary: '#f1f5f9',
                surface: '#ffffff',
                background: '#f8fafc',
            },
            fontFamily: {
                sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
            },
        },
    },
    plugins: [],
}
