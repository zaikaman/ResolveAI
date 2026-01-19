/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        container: {
            center: true,
            padding: {
                DEFAULT: '1rem',
                md: '2rem',
                lg: '1rem',
                xl: '1rem',
            },
        },
        extend: {

            colors: {
                'color-slate-500': '#64748b',
                'color-slate-600': '#475569',
                'color-slate-700': '#334155',
                'color-slate-800': '#1e293b',
                "main": '#2563EB', // Blue 600
                "main2": '#DBEAFE', // Blue 100
                "main3": '#EFF6FF', // Blue 50
                "shadowcolor": '#93C5FD', // Blue 300
                // Progress/success colors (green)
                progress: {
                    50: '#f0fdf4',
                    100: '#dcfce7',
                    200: '#bbf7d0',
                    300: '#86efac',
                    400: '#4ade80',
                    500: '#22c55e',
                    600: '#16a34a',
                    700: '#15803d',
                    800: '#166534',
                    900: '#14532d',
                },
                // Encouragement/warm colors
                warm: {
                    50: '#fef3c7',
                    100: '#fde68a',
                    200: '#fcd34d',
                    300: '#fbbf24',
                    400: '#f59e0b',
                    500: '#f97316',
                    600: '#ea580c',
                    700: '#dc2626',
                    800: '#b91c1c',
                    900: '#991b1b',
                },
            },
            fontSize: {
                xxl: ['40px', '55px'],
            },
        },
    },
    plugins: [],
}
