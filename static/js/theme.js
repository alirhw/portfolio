/**
 * Unified Theme Manager
 * Supports UI toggle and Terminal command synchronization with localStorage persistence.
 */

export const THEME_KEY = 'portfolio_theme';
export const THEMES = Object.freeze({
    LIGHT: 'light',
    DARK: 'dark'
});

export class ThemeManager {
    static getSystemPreference() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches
            ? THEMES.DARK
            : THEMES.LIGHT;
    }

    static getCurrentTheme() {
        const stored = localStorage.getItem(THEME_KEY);
        if (stored === THEMES.LIGHT || stored === THEMES.DARK) {
            return stored;
        }
        return document.documentElement.getAttribute('data-theme') || this.getSystemPreference();
    }

    /**
     * Apply target theme and dispatch custom themechange event for cross-component sync.
     * @param {'light' | 'dark'} theme 
     */
    static setTheme(theme) {
        const targetTheme = (theme === THEMES.DARK) ? THEMES.DARK : THEMES.LIGHT;
        document.documentElement.setAttribute('data-theme', targetTheme);
        localStorage.setItem(THEME_KEY, targetTheme);

        // Update ARIA label on header button
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            const nextTheme = targetTheme === THEMES.LIGHT ? THEMES.DARK : THEMES.LIGHT;
            toggleBtn.setAttribute('aria-label', `Switch to ${nextTheme} theme`);
        }

        // Dispatch global theme change event
        window.dispatchEvent(new CustomEvent('themechange', { detail: { theme: targetTheme } }));
        return targetTheme;
    }

    /**
     * Switch between light and dark themes.
     */
    static toggleTheme() {
        const current = this.getCurrentTheme();
        const next = current === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK;
        return this.setTheme(next);
    }

    /**
     * Initialize theme settings on page load.
     */
    static init() {
        const initial = this.getCurrentTheme();
        this.setTheme(initial);

        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => {
                this.toggleTheme();
            });
        }

        // Listen for OS system theme changes if not manually overridden
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem(THEME_KEY)) {
                this.setTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
            }
        });
    }
}
