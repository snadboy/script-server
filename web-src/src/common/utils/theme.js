/**
 * Theme management utility for light/dark/system theme support.
 * Stores preference in localStorage and respects system preference when set to 'system'.
 */

const STORAGE_KEY = 'script_server_theme';
const VALID_THEMES = ['light', 'dark', 'system'];

let systemPreferenceMediaQuery = null;

/**
 * Get the current theme preference from localStorage.
 * @returns {'light' | 'dark' | 'system'} The stored theme preference, defaults to 'system'.
 */
export function getThemePreference() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored && VALID_THEMES.includes(stored)) {
        return stored;
    }
    return 'system';
}

/**
 * Set the theme preference and apply it.
 * @param {'light' | 'dark' | 'system'} theme - The theme preference to set.
 */
export function setThemePreference(theme) {
    if (!VALID_THEMES.includes(theme)) {
        console.warn(`Invalid theme: ${theme}. Using 'system' instead.`);
        theme = 'system';
    }
    localStorage.setItem(STORAGE_KEY, theme);
    applyTheme();
}

/**
 * Get the effective theme (resolved from 'system' to actual value).
 * @returns {'light' | 'dark'} The actual theme to use.
 */
export function getEffectiveTheme() {
    const preference = getThemePreference();
    if (preference === 'system') {
        return getSystemPreference();
    }
    return preference;
}

/**
 * Get the system's preferred color scheme.
 * @returns {'light' | 'dark'} The system preference.
 */
export function getSystemPreference() {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
        return 'dark';
    }
    return 'light';
}

/**
 * Apply the current theme to the document.
 */
export function applyTheme() {
    const effectiveTheme = getEffectiveTheme();
    document.documentElement.setAttribute('data-theme', effectiveTheme);
}

/**
 * Initialize theme system - apply theme and set up system preference listener.
 * Call this once when the app starts.
 */
export function initTheme() {
    applyTheme();

    // Listen for system preference changes
    if (window.matchMedia) {
        systemPreferenceMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        systemPreferenceMediaQuery.addEventListener('change', () => {
            // Only re-apply if user preference is 'system'
            if (getThemePreference() === 'system') {
                applyTheme();
            }
        });
    }
}

/**
 * Cycle through themes: light -> dark -> system -> light...
 * @returns {'light' | 'dark' | 'system'} The new theme preference.
 */
export function cycleTheme() {
    const current = getThemePreference();
    const next = current === 'light' ? 'dark' : current === 'dark' ? 'system' : 'light';
    setThemePreference(next);
    return next;
}

/**
 * Get the icon name for a theme preference.
 * @param {'light' | 'dark' | 'system'} theme - The theme preference.
 * @returns {string} The Material Icons icon name.
 */
export function getThemeIcon(theme) {
    switch (theme) {
        case 'light':
            return 'light_mode';
        case 'dark':
            return 'dark_mode';
        case 'system':
        default:
            return 'contrast';
    }
}

/**
 * Get the display label for a theme preference.
 * @param {'light' | 'dark' | 'system'} theme - The theme preference.
 * @returns {string} The display label.
 */
export function getThemeLabel(theme) {
    switch (theme) {
        case 'light':
            return 'Light';
        case 'dark':
            return 'Dark';
        case 'system':
        default:
            return 'System';
    }
}
