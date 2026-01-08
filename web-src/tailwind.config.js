/** @type {import('tailwindcss').Config} */
module.exports = {
  purge: [
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './public/index.html'
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary colors (teal)
        primary: {
          DEFAULT: 'var(--primary-color)',
          dark: 'var(--primary-color-dark-color)',
          light: 'var(--primary-color-light-color)',
          hover: 'var(--primary-color-raised-hover-solid)',
          focus: 'var(--primary-color-raised-focus-solid)'
        },
        // Surface and background
        surface: 'var(--surface-color)',
        background: {
          DEFAULT: 'var(--background-color)',
          emphasis: 'var(--background-color-high-emphasis)',
          subtle: 'var(--background-color-slight-emphasis)',
          disabled: 'var(--background-color-disabled)',
          '4dp': 'var(--background-color-level-4dp)',
          '8dp': 'var(--background-color-level-8dp)',
          '16dp': 'var(--background-color-level-16dp)'
        },
        // Text colors
        text: {
          DEFAULT: 'var(--font-color-main)',
          medium: 'var(--font-color-medium)',
          disabled: 'var(--font-color-disabled)',
          'on-primary': 'var(--font-on-primary-color-main)',
          'on-primary-medium': 'var(--font-on-primary-color-medium)'
        },
        // Semantic colors
        error: 'var(--error-color)',
        separator: 'var(--separator-color)',
        outline: 'var(--outline-color)',
        // Interaction states
        hover: 'var(--hover-color)',
        focus: 'var(--focus-color)'
      },
      // Standardized spacing scale
      spacing: {
        '18': '4.5rem',    // 72px
        '88': '22rem',     // 352px - sidebar width
        '300': '300px'     // sidebar width
      },
      // Font sizes with line-height
      fontSize: {
        'xs': ['0.75rem', { lineHeight: '1rem' }],      // 12px
        'sm': ['0.875rem', { lineHeight: '1.25rem' }],  // 14px
        'base': ['1rem', { lineHeight: '1.5rem' }],     // 16px
        'lg': ['1.125rem', { lineHeight: '1.75rem' }],  // 18px
        'xl': ['1.25rem', { lineHeight: '1.75rem' }],   // 20px
        '2xl': ['1.5rem', { lineHeight: '2rem' }],      // 24px
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }]    // 36px
      },
      // Border radius
      borderRadius: {
        'sm': '2px',
        'DEFAULT': '4px',
        'md': '6px',
        'lg': '8px',
        'xl': '12px'
      },
      // Box shadows matching existing system
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'DEFAULT': 'var(--shadow-4dp)',
        'md': 'var(--shadow-6dp)',
        'lg': 'var(--shadow-8dp)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)',
        'none': 'none'
      },
      // Font family
      fontFamily: {
        'sans': ['Roboto', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Helvetica', 'Arial', 'sans-serif'],
        'mono': ['Roboto Mono', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', 'monospace']
      },
      // Min/Max widths
      minWidth: {
        'sidebar': '300px'
      },
      maxWidth: {
        'sidebar': '300px'
      },
      // Transition durations
      transitionDuration: {
        '250': '250ms',
        '300': '300ms'
      },
      // Z-index scale
      zIndex: {
        'sidebar': '100',
        'overlay': '150',
        'modal': '200',
        'toast': '300'
      }
    }
  },
  plugins: [],
  // Disable preflight to avoid conflicts with Materialize during migration
  corePlugins: {
    preflight: false
  }
}
